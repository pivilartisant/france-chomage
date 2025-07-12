"""
Tests pour les modèles de données
"""
import pytest
from pydantic import ValidationError

from france_chomage.models import Job

class TestJobModel:
    """Tests pour le modèle Job"""
    
    def test_job_creation_valid(self):
        """Test création d'un Job valide"""
        job_data = {
            "title": "Développeur Python",
            "company": "TechCorp",
            "location": "Paris, France",
            "date_posted": "2024-01-15",
            "job_url": "https://example.com/job/123",
            "site": "indeed",
            "description": "Poste de développeur Python senior avec 5 ans d'expérience",
            "is_remote": "True",
            "salary_source": "50k-70k EUR"
        }
        
        job = Job(**job_data)
        
        assert job.title == "Développeur Python"
        assert job.company == "TechCorp"
        assert job.is_remote == True  # Conversion string -> bool
        assert job.site == "indeed"
    
    def test_job_required_fields(self):
        """Test que les champs obligatoires sont validés"""
        incomplete_data = {
            "title": "Dev",
            "company": "Corp"
            # Manque location, date_posted, job_url, site
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Job(**incomplete_data)
        
        errors = exc_info.value.errors()
        required_fields = {error["loc"][0] for error in errors}
        
        assert "location" in required_fields
        assert "date_posted" in required_fields
        assert "job_url" in required_fields
        assert "site" in required_fields
    
    def test_is_remote_parsing(self):
        """Test conversion is_remote string -> bool"""
        job_data_base = {
            "title": "Test",
            "company": "Test Corp",
            "location": "Paris",
            "date_posted": "2024-01-01",
            "job_url": "https://test.com",
            "site": "linkedin"
        }
        
        # Test string "True"
        job1 = Job(**{**job_data_base, "is_remote": "True"})
        assert job1.is_remote == True
        
        # Test string "false"
        job2 = Job(**{**job_data_base, "is_remote": "false"})
        assert job2.is_remote == False
        
        # Test bool direct
        job3 = Job(**{**job_data_base, "is_remote": True})
        assert job3.is_remote == True
    
    def test_short_description(self):
        """Test propriété short_description"""
        long_desc = "A" * 500  # Description longue
        
        job = Job(
            title="Test Job",
            company="Test Corp", 
            location="Paris",
            date_posted="2024-01-01",
            job_url="https://test.com",
            site="indeed",
            description=long_desc
        )
        
        assert len(job.short_description) <= 203  # 200 + "..."
        assert job.short_description.endswith("...")
    
    def test_display_title(self):
        """Test propriété display_title"""
        long_title = "Développeur " * 20  # Titre très long
        
        job = Job(
            title=long_title,
            company="Test Corp",
            location="Paris", 
            date_posted="2024-01-01",
            job_url="https://test.com",
            site="indeed"
        )
        
        assert len(job.display_title) <= 83  # 80 + "..."
        assert job.display_title.endswith("...")
    
    def test_clean_description(self):
        """Test nettoyage de la description"""
        messy_desc = "Texte avec\n\nmultiples\n\n\nretours\n\nà la ligne"
        
        job = Job(
            title="Test",
            company="Test Corp",
            location="Paris",
            date_posted="2024-01-01", 
            job_url="https://test.com",
            site="indeed",
            description=messy_desc
        )
        
        # Les retours à la ligne multiples doivent être nettoyés
        assert "\n\n" not in job.description
        assert job.description == "Texte avec multiples retours à la ligne"
    
    def test_strip_whitespace(self):
        """Test suppression des espaces en début/fin"""
        job = Job(
            title="  Développeur Python  ",
            company="  TechCorp  ",
            location="  Paris, France  ",
            date_posted="2024-01-01",
            job_url="https://test.com",
            site="indeed"
        )
        
        assert job.title == "Développeur Python"
        assert job.company == "TechCorp"  
        assert job.location == "Paris, France"
