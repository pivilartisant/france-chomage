"""
SQLAlchemy database models
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Date, Text, Index
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models"""
    pass

class Job(Base):
    """Database model for job postings"""
    __tablename__ = "jobs"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Required fields from original Job model
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    date_posted: Mapped[date] = mapped_column(Date, nullable=False)
    job_url: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    site: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Optional fields
    salary_source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    job_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    experience_range: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Job category for filtering
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Metadata fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    sent_to_telegram: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_job_url', 'job_url'),
        Index('idx_date_posted', 'date_posted'),
        Index('idx_category', 'category'),
        Index('idx_sent_to_telegram', 'sent_to_telegram'),
        Index('idx_created_at', 'created_at'),
        Index('idx_company_location', 'company', 'location'),
    )
    
    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}')>"
    
    @property
    def short_description(self) -> str:
        """Description courte pour Telegram (200 caractères)"""
        if not self.description:
            return ""
        return self.description[:200] + "..." if len(self.description) > 200 else self.description
    
    @property
    def display_title(self) -> str:
        """Titre nettoyé pour affichage"""
        return self.title[:80] + "..." if len(self.title) > 80 else self.title
    
    @property
    def formatted_date(self) -> str:
        """Date formatée en dd/mm/yyyy"""
        return self.date_posted.strftime("%d/%m/%Y")
