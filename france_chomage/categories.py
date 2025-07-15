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
    schedule_hour: int
    enabled: bool = True
    custom_scraper_class: Optional[str] = None
    max_results: Optional[int] = None
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.name:
            raise ValueError("Category name cannot be empty")
        if not self.search_terms:
            raise ValueError("Search terms cannot be empty")
        if not (0 <= self.schedule_hour <= 23):
            raise ValueError("Schedule hour must be between 0 and 23")
        if self.telegram_topic_id <= 0:
            raise ValueError("Telegram topic ID must be positive")


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
                    schedule_hour=config['schedule_hour'],
                    enabled=config.get('enabled', True),
                    custom_scraper_class=config.get('custom_scraper_class'),
                    max_results=config.get('max_results')
                )
                self._categories[name] = category_config
            
            self._validate_configuration()
            self._loaded = True
            print(f"✅ Loaded {len(self._categories)} categories from {config_file}")
            
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
        
        # Check for conflicting schedule hours (optional warning)
        schedule_hours = [cat.schedule_hour for cat in self._categories.values() if cat.enabled]
        if len(schedule_hours) != len(set(schedule_hours)):
            duplicates = [hour for hour in set(schedule_hours) if schedule_hours.count(hour) > 1]
            print(f"⚠️ Warning: Multiple categories scheduled at same hour: {duplicates}")
        
        # Validation complete - using categories.yml as single source of truth
        print("💡 All topic IDs are managed through categories.yml")
    
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
