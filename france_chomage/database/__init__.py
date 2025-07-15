"""
Database module for job storage and management
"""
from .models import Job, Base
from .connection import get_database_url, create_engine, get_session, initialize_database
from .repository import JobRepository
from .manager import JobManager, job_manager
from .migration_utils import (
    migrate_json_to_database,
    migrate_all_json_files,
    create_tables_if_not_exist,
    backup_jobs_to_json,
    get_migration_status,
    print_migration_status
)

__all__ = [
    "Job", 
    "Base", 
    "get_database_url", 
    "create_engine", 
    "get_session",
    "initialize_database",
    "JobRepository", 
    "JobManager", 
    "job_manager",
    "migrate_json_to_database",
    "migrate_all_json_files", 
    "create_tables_if_not_exist",
    "backup_jobs_to_json",
    "get_migration_status",
    "print_migration_status"
]
