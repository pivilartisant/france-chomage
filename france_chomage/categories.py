"""
Configuration-driven category management system
"""
import os
import yaml
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from pathlib import Path


@dataclass
class CategoryConfig:
    """Configuration for a job category"""
    name: str
    search_terms: str
    telegram_topic_id: int
    schedule_hour: int  # Deprecated - use scrape_hours and send_hours
    enabled: bool = True
    custom_scraper_class: Optional[str] = None
    max_results: Optional[int] = None
    scrape_hours: Optional[List[int]] = None
    send_hours: Optional[List[int]] = None
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.name:
            raise ValueError("Category name cannot be empty")
        if not self.search_terms:
            raise ValueError("Search terms cannot be empty")
        if self.telegram_topic_id <= 0:
            raise ValueError("Telegram topic ID must be positive")
        
        # Handle backward compatibility and new format
        if self.scrape_hours is None and self.send_hours is None:
            # Legacy format - use schedule_hour for both
            if not (0 <= self.schedule_hour <= 23):
                raise ValueError("Schedule hour must be between 0 and 23")
            self.scrape_hours = [self.schedule_hour]
            self.send_hours = [self.schedule_hour]
        else:
            # New format - validate separate hours
            if self.scrape_hours is None:
                self.scrape_hours = [self.schedule_hour]
            if self.send_hours is None:
                self.send_hours = [self.schedule_hour]
            
            # Validate hours
            for hour in self.scrape_hours:
                if not (0 <= hour <= 23):
                    raise ValueError(f"Scrape hour {hour} must be between 0 and 23")
            for hour in self.send_hours:
                if not (0 <= hour <= 23):
                    raise ValueError(f"Send hour {hour} must be between 0 and 23")


class CategoryManager:
    """Manages job categories configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "categories.yml"
        self._categories: Dict[str, CategoryConfig] = {}
        self._loaded = False
    
    def load_categories(self) -> None:
        """Load categories from configuration file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Categories configuration file not found: {config_file}")
        
        try:
            with config_file.open('r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'categories' not in data:
                raise ValueError("Invalid configuration: 'categories' section not found")
            
            self._categories = {}
            for name, config in data['categories'].items():
                category_config = CategoryConfig(
                    name=name,
                    search_terms=config['search_terms'],
                    telegram_topic_id=config['telegram_topic_id'],
                    schedule_hour=config.get('schedule_hour', 12),  # Default fallback
                    enabled=config.get('enabled', True),
                    custom_scraper_class=config.get('custom_scraper_class'),
                    max_results=config.get('max_results'),
                    scrape_hours=config.get('scrape_hours'),
                    send_hours=config.get('send_hours')
                )
                self._categories[name] = category_config
            
            self._validate_configuration()
            self._loaded = True
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading categories configuration: {e}")
    
    def _validate_configuration(self) -> None:
        """Validate the loaded configuration for conflicts and requirements"""
        if not self._categories:
            raise ValueError("No categories defined in configuration")
        
        # Check for duplicate telegram topic IDs
        topic_ids = [cat.telegram_topic_id for cat in self._categories.values() if cat.enabled]
        if len(topic_ids) != len(set(topic_ids)):
            duplicates = [tid for tid in set(topic_ids) if topic_ids.count(tid) > 1]
            raise ValueError(f"Duplicate Telegram topic IDs found: {duplicates}")
        
        # Check for conflicting scrape/send hours (optional warning)
        all_scrape_hours = []
        all_send_hours = []
        for cat in self._categories.values():
            if cat.enabled:
                all_scrape_hours.extend(cat.scrape_hours)
                all_send_hours.extend(cat.send_hours)
        
        # Note: Multiple categories can be scheduled at same hours - this is acceptable
        # as the system handles concurrent operations
        
        # Validation complete - using categories.yml as single source of truth
    
    def get_category(self, name: str) -> CategoryConfig:
        """Get configuration for a specific category"""
        if not self._loaded:
            self.load_categories()
        
        if name not in self._categories:
            raise ValueError(f"Category '{name}' not found in configuration")
        
        category = self._categories[name]
        if not category.enabled:
            raise ValueError(f"Category '{name}' is disabled")
        
        return category
    
    def get_topic_id(self, name: str) -> int:
        """Get the topic ID for a category from categories.yml"""
        category = self.get_category(name)
        return category.telegram_topic_id
    
    def get_all_categories(self) -> Dict[str, CategoryConfig]:
        """Get all category configurations"""
        if not self._loaded:
            self.load_categories()
        return self._categories.copy()
    
    def get_enabled_categories(self) -> Dict[str, CategoryConfig]:
        """Get only enabled category configurations"""
        if not self._loaded:
            self.load_categories()
        return {name: config for name, config in self._categories.items() if config.enabled}
    
    def get_category_names(self) -> List[str]:
        """Get list of all category names"""
        if not self._loaded:
            self.load_categories()
        return list(self._categories.keys())
    
    def get_enabled_category_names(self) -> List[str]:
        """Get list of enabled category names"""
        return list(self.get_enabled_categories().keys())
    
    def is_category_enabled(self, name: str) -> bool:
        """Check if a category is enabled"""
        try:
            category = self.get_category(name)
            return category.enabled
        except ValueError:
            return False
    
    def reload_categories(self) -> None:
        """Reload categories from configuration file"""
        self._loaded = False
        self.load_categories()


# Global instance
category_manager = CategoryManager()
