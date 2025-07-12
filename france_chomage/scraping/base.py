"""
Scraper de base avec logique commune
"""
import asyncio
import json
import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
import structlog

from jobspy import scrape_jobs
from france_chomage.config import settings
from france_chomage.environments import get_sites_for_environment, is_docker
from france_chomage.models import Job

logger = structlog.get_logger()

class ScraperBase(ABC):
    """Classe de base pour tous les scrapers"""
    
    # À définir dans les sous-classes
    search_terms: str
    filename_prefix: str
    job_type: str  # Pour les hashtags
    
    def __init__(self):
        self.logger = logger.bind(scraper=self.__class__.__name__)
    
    async def scrape(self) -> List[Job]:
        """Point d'entrée principal pour scraper"""
        self.logger.info("Début du scraping", job_type=self.job_type)
        
        jobs = await self._scrape_with_retry()
        
        if jobs:
            self.logger.info("Scraping terminé", jobs_count=len(jobs))
            self._save_jobs(jobs)
        else:
            self.logger.warning("Aucune offre trouvée")
            self._save_empty_file()
            
        return jobs or []
    
    async def _scrape_with_retry(self) -> Optional[List[Job]]:
        """Scrape avec logique de retry"""
        sites = get_sites_for_environment()
        self.logger.info("Stratégie de scraping", sites=sites, is_docker=is_docker())
        
        for attempt in range(1, settings.max_retries + 1):
            try:
                self.logger.info("Tentative de scraping", attempt=attempt)
                
                # Délai aléatoire anti-détection
                delay = random.uniform(settings.scrape_delay_min, settings.scrape_delay_max)
                self.logger.debug("Attente anti-détection", delay=delay)
                await asyncio.sleep(delay)
                
                # Paramètres de scraping
                scrape_params = {
                    'site_name': list(sites),
                    'search_term': self.search_terms,
                    'location': settings.location,
                    'results_wanted': settings.results_wanted,
                    'country_indeed': settings.country,
                }
                
                self.logger.debug("Paramètres de scraping", **scrape_params)
                
                # Scraping synchrone (jobspy n'est pas async)
                df = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: scrape_jobs(**scrape_params)
                )
                
                if df is not None and len(df) > 0:
                    jobs = self._dataframe_to_jobs(df)
                    self.logger.info("Scraping réussi", jobs_found=len(jobs))
                    return jobs
                else:
                    self.logger.warning("Aucune offre trouvée", attempt=attempt)
                    
            except Exception as exc:
                self.logger.error(
                    "Échec de la tentative",
                    attempt=attempt,
                    error=str(exc),
                    exc_info=True
                )
                
                if attempt < settings.max_retries:
                    wait_time = settings.retry_delay_base * attempt
                    self.logger.info("Attente avant nouvelle tentative", wait_time=wait_time)
                    await asyncio.sleep(wait_time)
        
        self.logger.error("Toutes les tentatives ont échoué")
        return None
    
    def _dataframe_to_jobs(self, df) -> List[Job]:
        """Convertit le DataFrame pandas en liste de Jobs"""
        jobs = []
        for _, row in df.iterrows():
            try:
                job_data = row.to_dict()
                # Nettoie les valeurs NaN/None
                job_data = {k: v for k, v in job_data.items() if v is not None and str(v) != 'nan'}
                
                # Convertit date_posted en string si c'est un objet date/datetime
                if 'date_posted' in job_data and hasattr(job_data['date_posted'], 'strftime'):
                    job_data['date_posted'] = job_data['date_posted'].strftime('%Y-%m-%d')
                
                # Ajoute une date par défaut si manquante
                if 'date_posted' not in job_data:
                    from datetime import date
                    job_data['date_posted'] = date.today().strftime('%Y-%m-%d')
                
                job = Job(**job_data)
                jobs.append(job)
            except Exception as exc:
                self.logger.warning("Erreur parsing job", error=str(exc), job_data=list(job_data.keys()))
                continue
        
        return jobs
    
    def _save_jobs(self, jobs: List[Job]) -> None:
        """Sauvegarde les jobs en JSON"""
        output_path = Path(f"jobs_{self.filename_prefix}.json")
        
        jobs_data = [job.dict() for job in jobs]
        
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(jobs_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info("Jobs sauvegardés", file=str(output_path), count=len(jobs))
    
    def _save_empty_file(self) -> None:
        """Sauvegarde un fichier vide en cas d'échec"""
        output_path = Path(f"jobs_{self.filename_prefix}.json")
        
        with output_path.open('w', encoding='utf-8') as f:
            json.dump([], f)
        
        self.logger.info("Fichier vide créé", file=str(output_path))
    
    @classmethod
    def load_jobs(cls) -> List[Job]:
        """Charge les jobs depuis le fichier JSON"""
        # Utilise la valeur de filename_prefix de la classe
        filename_prefix = getattr(cls, 'filename_prefix', 'jobs')
        file_path = Path(f"jobs_{filename_prefix}.json")
        
        if not file_path.exists():
            logger.warning("Fichier de jobs introuvable", file=str(file_path))
            return []
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            jobs = [Job(**job_data) for job_data in data]
            logger.info("Jobs chargés", file=str(file_path), count=len(jobs))
            return jobs
            
        except Exception as exc:
            logger.error("Erreur chargement jobs", file=str(file_path), error=str(exc))
            return []
