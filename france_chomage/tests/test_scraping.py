"""
Tests pour les scrapers
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import pandas as pd

from france_chomage.scraping.category_scraper import CategoryScraper, create_category_scraper
from france_chomage.categories import CategoryConfig
from france_chomage.models import Job

@pytest.fixture
def sample_dataframe():
    """DataFrame de test comme retourné par jobspy"""
    data = {
        'title': ['Dev Python', 'Designer UI'],
        'company': ['TechCorp', 'DesignStudio'], 
        'location': ['Paris', 'Lyon'],
        'date_posted': ['2024-01-15', '2024-01-16'],
        'job_url': ['https://test1.com', 'https://test2.com'],
        'site': ['indeed', 'linkedin'],
        'description': ['Description job 1', 'Description job 2'],
        'is_remote': ['True', 'False'],
        'salary_source': ['50k EUR', None]
    }
    return pd.DataFrame(data)

@pytest.fixture
def communication_config():
    """Configuration pour les tests de communication"""
    return CategoryConfig(
        name="communication",
        search_terms="communication",
        telegram_topic_id=3,
        schedule_hour=17,
        enabled=True
    )

@pytest.fixture
def design_config():
    """Configuration pour les tests de design"""
    return CategoryConfig(
        name="design",
        search_terms="design graphique OR graphiste OR UI UX OR designer",
        telegram_topic_id=40,
        schedule_hour=18,
        enabled=True
    )

class TestScraperBase:
    """Tests pour la classe de base ScraperBase"""
    
    @pytest.mark.asyncio
    async def test_dataframe_to_jobs(self, sample_dataframe, communication_config):
        """Test conversion DataFrame -> List[Job]"""
        scraper = CategoryScraper(communication_config)
        
        jobs = scraper._dataframe_to_jobs(sample_dataframe)
        
        assert len(jobs) == 2
        assert all(isinstance(job, Job) for job in jobs)
        
        # Vérifications du premier job
        job1 = jobs[0]
        assert job1.title == "Dev Python"
        assert job1.company == "TechCorp"
        assert job1.is_remote == True
        assert job1.salary_source == "50k EUR"
        
        # Vérifications du deuxième job
        job2 = jobs[1]
        assert job2.title == "Designer UI"
        assert job2.is_remote == False
        assert job2.salary_source is None
    
    @pytest.mark.asyncio
    async def test_dataframe_to_jobs_invalid_data(self, communication_config):
        """Test gestion des données invalides dans le DataFrame"""
        # DataFrame avec données invalides
        invalid_data = {
            'title': ['Job valide', None, 'Job sans URL'],
            'company': ['Corp1', 'Corp2', 'Corp3'],
            'location': ['Paris', 'Lyon', 'Lille'],
            'date_posted': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'job_url': ['https://valid.com', 'https://valid2.com', None],  # URL manquante
            'site': ['indeed', 'linkedin', 'indeed']
        }
        df = pd.DataFrame(invalid_data)
        
        scraper = CategoryScraper(communication_config)
        jobs = scraper._dataframe_to_jobs(df)
        
        # Seuls les jobs valides doivent être conservés
        assert len(jobs) == 1  # Job avec title=None et job sans URL exclus
        assert all(job.title for job in jobs)
        assert all(job.job_url for job in jobs)
    
    @pytest.mark.asyncio
    @patch('france_chomage.scraping.base.asyncio.get_event_loop')
    @patch('france_chomage.scraping.base.get_sites_for_environment')
    async def test_scrape_with_retry_success(self, mock_sites, mock_loop, sample_dataframe, communication_config):
        """Test scraping réussi"""
        mock_sites.return_value = ("linkedin",)
        
        # Mock executor
        mock_executor = AsyncMock()
        mock_executor.return_value = sample_dataframe
        mock_loop.return_value.run_in_executor = mock_executor
        
        scraper = CategoryScraper(communication_config)
        
        jobs = await scraper._scrape_with_retry()
        
        assert jobs is not None
        assert len(jobs) == 2
        assert all(isinstance(job, Job) for job in jobs)
    
    @pytest.mark.asyncio
    @patch('france_chomage.scraping.base.asyncio.get_event_loop')
    @patch('france_chomage.scraping.base.get_sites_for_environment')
    async def test_scrape_with_retry_failure(self, mock_sites, mock_loop, communication_config):
        """Test échec de scraping après tous les retries"""
        mock_sites.return_value = ("linkedin",)
        
        # Mock executor qui échoue toujours
        mock_executor = AsyncMock()
        mock_executor.side_effect = Exception("Network error")
        mock_loop.return_value.run_in_executor = mock_executor
        
        scraper = CategoryScraper(communication_config)
        
        jobs = await scraper._scrape_with_retry()
        
        assert jobs is None
        # Vérification que les retries ont été tentés
        assert mock_executor.call_count == 3  # max_retries par défaut
    
    @pytest.mark.asyncio
    async def test_save_jobs(self, tmp_path, communication_config):
        """Test sauvegarde des jobs"""
        # Change vers répertoire temporaire pour les tests
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            jobs = [
                Job(
                    title="Test Job",
                    company="Test Corp", 
                    location="Paris",
                    date_posted="2024-01-01",
                    job_url="https://test.com",
                    site="indeed"
                )
            ]
            
            scraper = CategoryScraper(communication_config)
            scraper._save_jobs(jobs)
            
            # Vérification que le fichier est créé
            output_file = tmp_path / "jobs_communication.json"
            assert output_file.exists()
            
            # Vérification du contenu
            import json
            with output_file.open() as f:
                data = json.load(f)
            
            assert len(data) == 1
            assert data[0]['title'] == "Test Job"
            
        finally:
            os.chdir(original_cwd)
    
    @pytest.mark.asyncio
    async def test_save_empty_file(self, tmp_path, design_config):
        """Test sauvegarde fichier vide"""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            scraper = CategoryScraper(design_config)
            scraper._save_empty_file()
            
            output_file = tmp_path / "jobs_design.json"
            assert output_file.exists()
            
            import json
            with output_file.open() as f:
                data = json.load(f)
            
            assert data == []
            
        finally:
            os.chdir(original_cwd)

class TestCategoryScraper:
    """Tests spécifiques au scraper de configuration"""
    
    def test_communication_scraper_attributes(self, communication_config):
        """Test attributs du scraper communication"""
        scraper = CategoryScraper(communication_config)
        
        assert scraper.search_terms == "communication"
        assert scraper.filename_prefix == "communication" 
        assert scraper.job_type == "communication"
        assert scraper.category_config == communication_config

    def test_design_scraper_attributes(self, design_config):
        """Test attributs du scraper design"""
        scraper = CategoryScraper(design_config)
        
        assert scraper.search_terms == "design graphique OR graphiste OR UI UX OR designer"
        assert scraper.filename_prefix == "design"
        assert scraper.job_type == "design"
        assert scraper.category_config == design_config

    def test_scraper_factory(self, communication_config):
        """Test factory de création de scrapers"""
        scraper = create_category_scraper(communication_config)
        
        assert isinstance(scraper, CategoryScraper)
        assert scraper.search_terms == "communication"
        assert scraper.job_type == "communication"

    def test_max_results_override(self):
        """Test override du max_results"""
        config = CategoryConfig(
            name="test",
            search_terms="test",
            telegram_topic_id=999,
            schedule_hour=10,
            enabled=True,
            max_results=25
        )
        
        scraper = CategoryScraper(config)
        assert hasattr(scraper, '_override_max_results')
        assert scraper._override_max_results == 25
