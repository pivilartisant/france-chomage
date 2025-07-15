"""
Database manager for job operations with caching and filtering
"""
from datetime import date, datetime, timedelta
from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Job as DBJob
from .repository import JobRepository
from . import connection
from ..models import Job as PydanticJob

class JobManager:
    """High-level job management with caching and filtering"""
    
    def __init__(self):
        self._job_cache: Set[str] = set()  # Cache of job URLs to prevent duplicates
        self._cache_loaded = False
    
    async def _ensure_cache_loaded(self, session: AsyncSession):
        """Load job URLs into cache for duplicate detection"""
        if self._cache_loaded:
            return
        
        repository = JobRepository(session)
        # Load recent job URLs (last 7 days) into cache
        recent_jobs = await repository.get_recent_jobs(hours=7*24)
        self._job_cache = {job.job_url for job in recent_jobs}
        self._cache_loaded = True
        print(f"🔧 Loaded {len(self._job_cache)} recent job URLs into cache")
    
    async def process_scraped_jobs(
        self, 
        jobs: List[PydanticJob], 
        category: str,
        max_age_days: int = 30
    ) -> tuple[List[DBJob], int]:
        """
        Process scraped jobs: filter by date, check for duplicates, save new ones
        Returns: (new_jobs_saved, total_filtered_out)
        """
        if not jobs:
            return [], 0
        
        connection.initialize_database()
        if connection.async_session_factory is None:
            raise RuntimeError("Database not properly initialized")
            
        async with connection.async_session_factory() as session:
            await self._ensure_cache_loaded(session)
            repository = JobRepository(session)
            
            # Filter jobs by date (only last 30 days)
            cutoff_date = date.today() - timedelta(days=max_age_days)
            recent_jobs = []
            
            for job in jobs:
                try:
                    job_date = datetime.strptime(job.date_posted, "%Y-%m-%d").date()
                    if job_date >= cutoff_date:
                        recent_jobs.append(job)
                except ValueError:
                    # Skip jobs with invalid dates
                    continue
            
            print(f"📅 Filtered to {len(recent_jobs)} jobs from last {max_age_days} days (from {len(jobs)} total)")
            
            # Check for duplicates and save new jobs
            new_jobs = []
            duplicate_count = 0
            
            for job in recent_jobs:
                # Check cache first (faster)
                if job.job_url in self._job_cache:
                    duplicate_count += 1
                    continue
                
                # Check database (slower but thorough)
                if await repository.job_exists(job.job_url):
                    duplicate_count += 1
                    self._job_cache.add(job.job_url)  # Add to cache for next time
                    continue
                
                try:
                    # Save new job
                    db_job = await repository.create_job(job, category)
                    new_jobs.append(db_job)
                    self._job_cache.add(job.job_url)  # Add to cache
                    
                except Exception as exc:
                    print(f"⚠️ Error saving job {job.title}: {exc}")
                    continue
            
            filtered_count = len(jobs) - len(recent_jobs) + duplicate_count
            print(f"💾 Saved {len(new_jobs)} new jobs, skipped {duplicate_count} duplicates")
            
            return new_jobs, filtered_count
    
    async def get_unsent_jobs(self, category: str, max_age_days: int = 30) -> List[DBJob]:
        """Get jobs that haven't been sent to Telegram yet"""
        connection.initialize_database()
        if connection.async_session_factory is None:
            raise RuntimeError("Database not properly initialized")
        async with connection.async_session_factory() as session:
            repository = JobRepository(session)
            return await repository.get_jobs_by_category(
                category=category,
                days_limit=max_age_days,
                only_unsent=True
            )
    
    async def mark_jobs_as_sent(self, job_ids: List[int]) -> int:
        """Mark jobs as sent to Telegram"""
        if not job_ids:
            return 0
        
        connection.initialize_database()
        if connection.async_session_factory is None:
            raise RuntimeError("Database not properly initialized")
        async with connection.async_session_factory() as session:
            repository = JobRepository(session)
            return await repository.mark_as_sent(job_ids)
    
    async def get_job_stats(self, days: int = 30) -> dict:
        """Get comprehensive job statistics"""
        connection.initialize_database()
        if connection.async_session_factory is None:
            raise RuntimeError("Database not properly initialized")
        async with connection.async_session_factory() as session:
            repository = JobRepository(session)
            return await repository.get_job_stats(days)
    
    async def cleanup_old_jobs(self, days_to_keep: int = 90) -> int:
        """Remove old jobs from database"""
        connection.initialize_database()
        if connection.async_session_factory is None:
            raise RuntimeError("Database not properly initialized")
        async with connection.async_session_factory() as session:
            repository = JobRepository(session)
            return await repository.cleanup_old_jobs(days_to_keep)
    
    def clear_cache(self):
        """Clear the internal job cache"""
        self._job_cache.clear()
        self._cache_loaded = False
        print("🔧 Job cache cleared")

# Global job manager instance
job_manager = JobManager()
