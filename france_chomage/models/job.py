"""
Modèle de données pour les offres d'emploi
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Job(BaseModel):
    """Modèle d'une offre d'emploi"""
    
    # Champs obligatoires
    title: str = Field(..., description="Titre du poste")
    company: str = Field(..., description="Nom de l'entreprise") 
    location: str = Field(..., description="Lieu du poste")
    date_posted: str = Field(..., description="Date de publication")
    job_url: str = Field(..., description="URL de l'offre")
    site: str = Field(..., description="Site source (indeed, linkedin)")
    
    # Champs optionnels
    salary_source: Optional[str] = Field(None, description="Information salaire")
    description: Optional[str] = Field(None, description="Description du poste")
    is_remote: bool = Field(False, description="Télétravail possible")
    job_type: Optional[str] = Field(None, description="Type de contrat")
    company_industry: Optional[str] = Field(None, description="Secteur d'activité")
    experience_range: Optional[str] = Field(None, description="Expérience requise")
    
    @field_validator('title', 'company', 'location')
    @classmethod
    def strip_whitespace(cls, v):
        """Nettoie les espaces en début/fin"""
        return v.strip() if v else v
    
    @field_validator('is_remote', mode='before')
    @classmethod
    def parse_is_remote(cls, v):
        """Parse is_remote depuis string 'True'/'False'"""
        if isinstance(v, str):
            return v.lower() == 'true'
        return bool(v)
    
    @field_validator('description')
    @classmethod
    def clean_description(cls, v):
        """Nettoie la description"""
        if not v:
            return v
        # Remplace les retours à la ligne multiples par des espaces
        cleaned = ' '.join(v.split())
        # Limite la longueur pour Telegram
        return cleaned[:1000] if len(cleaned) > 1000 else cleaned
    
    @property
    def short_description(self) -> str:
        """Description courte pour Telegram (200 caractères)"""
        if not self.description:
            return ""
        return self.description[:200] + "..." if len(self.description) > 200 else self.description
    
    @property
    def display_title(self) -> str:
        """Titre nettoyé pour affichage"""
        # Limite la longueur du titre
        return self.title[:80] + "..." if len(self.title) > 80 else self.title
        
    class Config:
        # Permet la création depuis dict pandas
        extra = "ignore"
        str_strip_whitespace = True
