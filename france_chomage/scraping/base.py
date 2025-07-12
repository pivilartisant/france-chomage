"""
Scraper de base avec logique commune
"""
import asyncio
import json
import random
from abc import ABC
from pathlib import Path
from typing import List, Optional

from jobspy import scrape_jobs
from france_chomage.config import settings
from france_chomage.environments import get_sites_for_environment, is_docker
from france_chomage.models import Job

class ScraperBase(ABC):
    """Classe de base pour tous les scrapers"""
    
    # À définir dans les sous-classes
    search_terms: str
    filename_prefix: str
    job_type: str  # Pour les hashtags
    
    def __init__(self):
        pass
    
    async def scrape(self) -> List[Job]:
        """Point d'entrée principal pour scraper"""
        print(f"🔍 Début du scraping {self.job_type}")
        
        jobs = await self._scrape_with_retry()
        
        if jobs:
            print(f"✅ Scraping terminé - {len(jobs)} offres trouvées")
            self._save_jobs(jobs)
        else:
            print("⚠️ Aucune offre trouvée")
            self._save_empty_file()
            
        return jobs or []
    
    async def _scrape_with_retry(self) -> Optional[List[Job]]:
        """Scrape avec logique de retry"""
        sites = get_sites_for_environment()
        env_type = 'Docker' if is_docker() else 'Local'
        print(f"🌐 Sites: {', '.join(sites)} ({env_type})")
        
        if 'indeed' in sites:
            print("⚠️ Indeed inclus - Risque de blocage 403 élevé")
        if env_type == 'Local' and len(sites) > 1:
            print("🏠 Mode Local détecté - Indeed + LinkedIn (plus de risques)")
        elif env_type == 'Docker':
            print("🐳 Mode Docker détecté - LinkedIn uniquement (plus stable)")
        
        for attempt in range(1, settings.max_retries + 1):
            try:
                print(f"🔄 Tentative {attempt}/{settings.max_retries}")
                
                # Délai aléatoire anti-détection (plus long pour Indeed)
                if 'indeed' in sites and attempt > 1:
                    # Délais plus longs après un échec avec Indeed
                    delay = random.uniform(5.0, 15.0)
                    print(f"⏳ Délai anti-Indeed: {delay:.1f}s")
                else:
                    delay = random.uniform(settings.scrape_delay_min, settings.scrape_delay_max)
                    print(f"⏳ Attente standard: {delay:.1f}s")
                await asyncio.sleep(delay)
                
                # Paramètres de scraping avec stratégies anti-détection
                scrape_params = {
                    'site_name': list(sites),
                    'search_term': self.search_terms,
                    'location': settings.location,
                    'results_wanted': min(settings.results_wanted, 10) if 'indeed' in sites else settings.results_wanted,
                    'country_indeed': settings.country,

                }
                
                # Réduction du nombre de résultats pour Indeed
                if 'indeed' in sites:
                    scrape_params['results_wanted'] = min(scrape_params['results_wanted'], settings.indeed_max_results)
                    print(f"🎯 Limitation Indeed: max {settings.indeed_max_results} résultats pour éviter la détection")
                
                print(f"📍 Recherche: '{self.search_terms}' à {settings.location} ({settings.results_wanted} résultats)")
                print(f"🌐 Sites ciblés: {', '.join(scrape_params['site_name'])}")
                print(f"🔧 Paramètres complets: {scrape_params}")
                
                # Scraping synchrone (jobspy n'est pas async)
                print("🚀 Lancement de jobspy...")
                df = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: scrape_jobs(**scrape_params)
                )
                print("📊 Réponse jobspy reçue")
                
                if df is not None and len(df) > 0:
                    print(f"📄 DataFrame reçu: {len(df)} lignes, colonnes: {list(df.columns)}")
                    jobs = self._dataframe_to_jobs(df)
                    print(f"🎉 Succès! {len(jobs)} offres récupérées après parsing")
                    return jobs
                else:
                    if df is None:
                        print(f"⚠️ DataFrame vide (None) - tentative {attempt}")
                    else:
                        print(f"⚠️ DataFrame sans données ({len(df)} lignes) - tentative {attempt}")
                    
            except Exception as exc:
                error_msg = str(exc)
                print(f"❌ Erreur tentative {attempt}: {error_msg}")
                
                # Détection des erreurs spécifiques
                if "403" in error_msg:
                    print("🚫 Erreur 403 détectée - Blocage anti-bot probable")
                    
                    # Fallback automatique vers LinkedIn uniquement
                    if 'indeed' in sites and 'linkedin' in sites and len(sites) > 1:
                        print("🔄 Fallback automatique: tentative avec LinkedIn uniquement...")
                        linkedin_only_params = scrape_params.copy()
                        linkedin_only_params['site_name'] = ['linkedin']
                        linkedin_only_params['results_wanted'] = settings.results_wanted  # Pas de limite pour LinkedIn
                        
                        try:
                            print("🔗 Tentative LinkedIn seul...")
                            df_linkedin = await asyncio.get_event_loop().run_in_executor(
                                None, lambda: scrape_jobs(**linkedin_only_params)
                            )
                            
                            if df_linkedin is not None and len(df_linkedin) > 0:
                                print(f"✅ Succès LinkedIn! {len(df_linkedin)} offres trouvées")
                                jobs = self._dataframe_to_jobs(df_linkedin)
                                return jobs
                            else:
                                print("⚠️ LinkedIn n'a pas retourné de résultats")
                        except Exception as linkedin_exc:
                            print(f"❌ Échec LinkedIn aussi: {linkedin_exc}")
                    
                    print("💡 Suggestions pour éviter les 403:")
                    print("   • Indeed bloque souvent les scrapers")
                    print("   • Utilisez DOCKER=1 pour LinkedIn uniquement")
                    print("   • Réduisez RESULTS_WANTED à 5-10")
                    print("   • Augmentez les délais entre scraping")
                elif "timeout" in error_msg.lower():
                    print("⏰ Timeout détecté - Connexion lente ou serveur surchargé")
                elif "connection" in error_msg.lower():
                    print("🌐 Problème de connexion réseau")
                
                print(f"🔍 Type d'erreur: {type(exc).__name__}")
                print(f"📝 Message complet: {repr(exc)}")
                
                if attempt < settings.max_retries:
                    wait_time = settings.retry_delay_base * attempt
                    print(f"🔄 Attente {wait_time}s avant nouvelle tentative...")
                    await asyncio.sleep(wait_time)
                else:
                    print("💥 Toutes les tentatives épuisées")
        
        print("💥 Toutes les tentatives ont échoué")
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
                print(f"⚠️ Erreur parsing job: {str(exc)}")
                continue
        
        return jobs
    
    def _save_jobs(self, jobs: List[Job]) -> None:
        """Sauvegarde les jobs en JSON"""
        output_path = Path(f"jobs_{self.filename_prefix}.json")
        
        jobs_data = [job.model_dump() for job in jobs]
        
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(jobs_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 {len(jobs)} jobs sauvegardés dans {output_path}")
    
    def _save_empty_file(self) -> None:
        """Sauvegarde un fichier vide en cas d'échec"""
        output_path = Path(f"jobs_{self.filename_prefix}.json")
        
        with output_path.open('w', encoding='utf-8') as f:
            json.dump([], f)
        
        print(f"📄 Fichier vide créé: {output_path}")
    
    @classmethod
    def load_jobs(cls) -> List[Job]:
        """Charge les jobs depuis le fichier JSON"""
        # Utilise la valeur de filename_prefix de la classe
        filename_prefix = getattr(cls, 'filename_prefix', 'jobs')
        file_path = Path(f"jobs_{filename_prefix}.json")
        
        if not file_path.exists():
            print(f"⚠️ Fichier de jobs introuvable: {file_path}")
            return []
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            jobs = [Job(**job_data) for job_data in data]
            print(f"📂 {len(jobs)} jobs chargés depuis {file_path}")
            return jobs
            
        except Exception as exc:
            print(f"❌ Erreur chargement jobs de {file_path}: {str(exc)}")
            return []
