"""
Tests pour le bot Telegram
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from datetime import date
from france_chomage.telegram.bot import TelegramJobBot
from france_chomage.database.models import Job as DBJob

@pytest.fixture
def sample_job():
    """Fixture avec un job de test (DB model)"""
    job = DBJob()
    job.id = 1
    job.title = "Développeur Python Senior"
    job.company = "TechCorp Innovation"
    job.location = "Paris, 75001"
    job.date_posted = date(2024, 1, 15)
    job.job_url = "https://example.com/jobs/python-dev-123"
    job.site = "indeed"
    job.description = "Nous recherchons un développeur Python expérimenté pour rejoindre notre équipe dynamique. Vous travaillerez sur des projets innovants..."
    job.is_remote = True
    job.salary_source = "55k-70k EUR"
    job.category = "communication"
    return job

@pytest.fixture
def mock_settings():
    """Mock des settings"""
    with patch('france_chomage.telegram.bot.settings') as mock:
        mock.telegram_bot_token = "test_token_123"
        mock.telegram_group_id = "-1001234567890"
        yield mock

class TestTelegramJobBot:
    """Tests pour TelegramJobBot"""
    
    def test_escape_markdown(self, mock_settings):
        """Test échappement des caractères MarkdownV2"""
        bot = TelegramJobBot()
        
        # Test caractères spéciaux
        text = "Test avec *gras* et [lien](url) et autres: -+=|{}"
        escaped = bot.escape_markdown(text)
        
        assert "\\*gras\\*" in escaped
        assert "\\[lien\\]" in escaped
        assert "\\-\\+\\=" in escaped
        assert "\\|\\{\\}" in escaped
    
    def test_escape_markdown_empty(self, mock_settings):
        """Test échappement texte vide"""
        bot = TelegramJobBot()
        
        assert bot.escape_markdown("") == ""
        assert bot.escape_markdown(None) == ""
    
    def test_format_job_message(self, mock_settings, sample_job):
        """Test formatage d'un message job"""
        bot = TelegramJobBot()
        
        message = bot.format_job_message(sample_job, "communication")
        
        # Vérifications du contenu
        assert "🎯 *Développeur Python Senior*" in message
        assert "🏢 *TechCorp Innovation*" in message
        assert "📍 Paris, 75001" in message
        assert "📅 Publié le : 2024\\-01\\-15" in message
        assert "🏠 Télétravail possible" in message
        assert "💰 55k\\-70k EUR" in message
        assert "[Postuler ici](https://example.com/jobs/python-dev-123)" in message
        assert "#indeed #communication #Paris #emploi" in message
        
        # Vérification de la description courte
        assert "📝" in message
        assert len(sample_job.short_description) <= 200
    
    def test_format_job_message_no_optional_fields(self, mock_settings):
        """Test formatage sans champs optionnels"""
        bot = TelegramJobBot()
        
        minimal_job = Job(
            title="Job simple",
            company="Corp",
            location="Paris",
            date_posted="2024-01-01",
            job_url="https://test.com",
            site="linkedin"
            # Pas de description, salary, is_remote
        )
        
        message = bot.format_job_message(minimal_job, "design")
        
        assert "🎯 *Job simple*" in message
        assert "🏠 Télétravail possible" not in message
        assert "💰" not in message
        assert "📝" not in message
        assert "#linkedin #design #Paris #emploi" in message
    
    @pytest.mark.asyncio
    async def test_send_job_success(self, mock_settings, sample_job):
        """Test envoi réussi d'un job"""
        bot = TelegramJobBot()
        bot.bot = AsyncMock()
        
        result = await bot.send_job(sample_job, topic_id=123, job_type="communication")
        
        assert result == True
        bot.bot.send_message.assert_called_once()
        
        call_args = bot.bot.send_message.call_args
        assert call_args.kwargs['chat_id'] == "-1001234567890"
        assert call_args.kwargs['message_thread_id'] == 123
        assert call_args.kwargs['parse_mode'] == 'MarkdownV2'
    
    @pytest.mark.asyncio
    async def test_send_job_markdown_fallback(self, mock_settings, sample_job):
        """Test fallback sans Markdown en cas d'erreur"""
        bot = TelegramJobBot()
        bot.bot = AsyncMock()
        
        # Première tentative échoue (Markdown), deuxième réussit (texte brut)
        bot.bot.send_message.side_effect = [Exception("Markdown error"), None]
        
        result = await bot.send_job(sample_job, topic_id=123, job_type="communication")
        
        assert result == True
        assert bot.bot.send_message.call_count == 2
        
        # Deuxième appel sans parse_mode
        second_call = bot.bot.send_message.call_args_list[1]
        assert 'parse_mode' not in second_call.kwargs
    
    @pytest.mark.asyncio
    async def test_send_job_total_failure(self, mock_settings, sample_job):
        """Test échec total d'envoi"""
        bot = TelegramJobBot()
        bot.bot = AsyncMock()
        
        # Les deux tentatives échouent
        bot.bot.send_message.side_effect = Exception("Network error")
        
        result = await bot.send_job(sample_job, topic_id=123, job_type="communication")
        
        assert result == False
        assert bot.bot.send_message.call_count == 2
    
    @pytest.mark.asyncio
    async def test_send_jobs_empty_list(self, mock_settings):
        """Test envoi liste vide"""
        bot = TelegramJobBot()
        
        result = await bot.send_jobs([], topic_id=123, job_type="communication")
        
        assert result == 0
    
    @pytest.mark.asyncio
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_send_jobs_rate_limiting(self, mock_sleep, mock_settings, sample_job):
        """Test rate limiting entre les envois"""
        bot = TelegramJobBot()
        bot.bot = AsyncMock()
        
        jobs = [sample_job, sample_job]  # 2 jobs identiques
        
        result = await bot.send_jobs(jobs, topic_id=123, job_type="communication")
        
        assert result == 2
        assert bot.bot.send_message.call_count == 2
        
        # Vérification du rate limiting (2 secondes entre envois)
        mock_sleep.assert_called_with(2)
        assert mock_sleep.call_count == 2  # Un sleep par job
    
    def test_long_title_truncation(self, mock_settings):
        """Test troncature des titres longs"""
        bot = TelegramJobBot()
        
        long_title = "A" * 100  # Titre très long
        job = Job(
            title=long_title,
            company="Corp",
            location="Paris",
            date_posted="2024-01-01",
            job_url="https://test.com",
            site="indeed"
        )
        
        message = bot.format_job_message(job, "design")
        
        # Le titre affiché doit être tronqué
        assert job.display_title in message
        assert len(job.display_title) <= 83  # 80 + "..."
