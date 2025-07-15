"""
Job repository for database operations
"""
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Job as DBJob
from ..models import Job as PydanticJob

class JobRepository:
    """Repository for job database operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_job(self, job_data: PydanticJob, category: str) -> DBJob:
        """Create a new job in the database"""
        # Convert Pydantic model to SQLAlchemy model
        db_job = DBJob(
            title=job_data.title,
            company=job_data.company,
            location=job_data.location,
            date_posted=datetime.strptime(job_data.date_posted, "%Y-%m-%d").date(),
            job_url=job_data.job_url,
            site=job_data.site,
            salary_source=job_data.salary_source,
            description=job_data.description,
            is_remote=job_data.is_remote,
            job_type=job_data.job_type,
            company_industry=job_data.company_industry,
            experience_range=job_data.experience_range,
            category=category,
        )
        
        self.session.add(db_job)
        await self.session.commit()
        await self.session.refresh(db_job)
        return db_job
    
    async def job_exists(self, job_url: str) -> bool:
        """Check if a job already exists by URL"""
        result = await self.session.execute(
            select(DBJob).where(DBJob.job_url == job_url)
        )
        return result.scalar_one_or_none() is not None
    
    async def get_jobs_by_category(
        self, 
        category: str, 
        days_limit: int = 30,
        only_unsent: bool = False
    ) -> List[DBJob]:
        """Get jobs by category with optional date filtering"""
        query = select(DBJob).where(DBJob.category == category)
        
        # Filter by date (last N days)
        if days_limit > 0:
            cutoff_date = date.today() - timedelta(days=days_limit)
            query = query.where(DBJob.date_posted >= cutoff_date)
        
        # Filter only unsent jobs
        if only_unsent:
            query = query.where(DBJob.sent_to_telegram == False)
        
        # Order by date posted (newest first)
        query = query.order_by(desc(DBJob.date_posted), desc(DBJob.created_at))
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_recent_jobs(self, hours: int = 24) -> List[DBJob]:
        """Get jobs created in the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        query = select(DBJob).where(DBJob.created_at >= cutoff_time)
        query = query.order_by(desc(DBJob.created_at))
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def mark_as_sent(self, job_ids: List[int]) -> int:
        """Mark jobs as sent to Telegram"""
        if not job_ids:
            return 0
        
        # Update multiple jobs at once
        from sqlalchemy import update
        stmt = update(DBJob).where(DBJob.id.in_(job_ids)).values(
            sent_to_telegram=True,
            sent_at=datetime.utcnow()
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
    
    async def search_similar_jobs(
        self, 
        title: str, 
        company: str, 
        days_back: int = 7
    ) -> List[DBJob]:
        """Search for similar jobs (basic duplicate detection)"""
        cutoff_date = date.today() - timedelta(days=days_back)
        
        query = select(DBJob).where(
            and_(
                DBJob.date_posted >= cutoff_date,
                or_(
                    and_(DBJob.title.ilike(f"%{title[:20]}%"), DBJob.company == company),
                    DBJob.title == title
                )
            )
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_job_stats(self, days: int = 30) -> dict:
        """Get job statistics for the last N days"""
        cutoff_date = date.today() - timedelta(days=days)
        
        # Total jobs
        total_query = select(DBJob).where(DBJob.date_posted >= cutoff_date)
        total_result = await self.session.execute(total_query)
        total_jobs = len(total_result.scalars().all())
        
        # Jobs by category
        from sqlalchemy import func
        category_query = select(
            DBJob.category,
            func.count(DBJob.id).label('count')
        ).where(DBJob.date_posted >= cutoff_date).group_by(DBJob.category)
        
        category_result = await self.session.execute(category_query)
        categories = {row.category: row.count for row in category_result}
        
        # Sent vs unsent
        sent_query = select(DBJob).where(
            and_(
                DBJob.date_posted >= cutoff_date,
                DBJob.sent_to_telegram == True
            )
        )
        sent_result = await self.session.execute(sent_query)
        sent_jobs = len(sent_result.scalars().all())
        
        return {
            "total_jobs": total_jobs,
            "sent_jobs": sent_jobs,
            "unsent_jobs": total_jobs - sent_jobs,
            "categories": categories,
            "period_days": days
        }
    
    async def cleanup_old_jobs(self, days_to_keep: int = 90) -> int:
        """Remove jobs older than specified days"""
        cutoff_date = date.today() - timedelta(days=days_to_keep)
        
        from sqlalchemy import delete
        stmt = delete(DBJob).where(DBJob.date_posted < cutoff_date)
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
