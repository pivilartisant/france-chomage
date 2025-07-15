"""
Migration utilities for database setup
"""
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import JobRepository
from ..models import Job as PydanticJob

async def migrate_json_to_database(session: AsyncSession, json_file_path: str, category: str) -> int:
    """Migrate jobs from JSON file to database"""
    file_path = Path(json_file_path)
    
    if not file_path.exists():
        print(f"⚠️ JSON file not found: {json_file_path}")
        return 0
    
    try:
        with file_path.open('r', encoding='utf-8') as f:
            jobs_data = json.load(f)
        
        if not jobs_data:
            print(f"📄 Empty JSON file: {json_file_path}")
            return 0
        
        repository = JobRepository(session)
        migrated_count = 0
        skipped_count = 0
        
        print(f"🔄 Migrating {len(jobs_data)} jobs from {json_file_path} to database...")
        
        for job_data in jobs_data:
            try:
                # Check if job already exists
                if await repository.job_exists(job_data['job_url']):
                    skipped_count += 1
                    continue
                
                # Convert to Pydantic model first for validation
                pydantic_job = PydanticJob(**job_data)
                
                # Create in database
                await repository.create_job(pydantic_job, category)
                migrated_count += 1
                
            except Exception as exc:
                print(f"⚠️ Error migrating job {job_data.get('title', 'Unknown')}: {exc}")
                continue
        
        print(f"✅ Migration complete: {migrated_count} jobs migrated, {skipped_count} skipped")
        return migrated_count
        
    except Exception as exc:
        print(f"❌ Error reading JSON file {json_file_path}: {exc}")
        return 0

async def migrate_all_json_files(session: AsyncSession) -> Dict[str, int]:
    """Migrate all existing JSON files to database"""
    categories = {
        "jobs_communication.json": "communication",
        "jobs_design.json": "design", 
        "jobs_restauration.json": "restauration"
    }
    
    results = {}
    
    for json_file, category in categories.items():
        count = await migrate_json_to_database(session, json_file, category)
        results[category] = count
    
    total_migrated = sum(results.values())
    print(f"🎉 Total migration complete: {total_migrated} jobs migrated across all categories")
    
    return results

def create_tables_sync():
    """Create database tables synchronously to avoid event loop conflicts"""
    import asyncio
    from .models import Base
    from . import connection
    
    def run_create_tables():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def _create():
                # Initialize database connection
                connection.initialize_database()
                
                if connection.engine is None:
                    raise RuntimeError("Database engine not properly initialized")
                
                # Create all tables
                async with connection.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                
                print("✅ Database tables created successfully")
            
            loop.run_until_complete(_create())
        finally:
            loop.close()
    
    run_create_tables()

async def create_tables_if_not_exist():
    """Create database tables if they don't exist - async version"""
    from .models import Base
    from . import connection
    
    # Initialize database connection
    connection.initialize_database()
    
    if connection.engine is None:
        raise RuntimeError("Database engine not properly initialized")
    
    # Create all tables
    async with connection.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully")

async def backup_jobs_to_json(session: AsyncSession, category: str, output_file: str = None) -> str:
    """Backup database jobs to JSON file"""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"backup_jobs_{category}_{timestamp}.json"
    
    repository = JobRepository(session)
    jobs = await repository.get_jobs_by_category(category, days_limit=0)  # All jobs
    
    # Convert to JSON-serializable format
    jobs_data = []
    for job in jobs:
        job_dict = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "date_posted": job.date_posted.strftime("%Y-%m-%d"),
            "job_url": job.job_url,
            "site": job.site,
            "salary_source": job.salary_source,
            "description": job.description,
            "is_remote": job.is_remote,
            "job_type": job.job_type,
            "company_industry": job.company_industry,
            "experience_range": job.experience_range,
        }
        jobs_data.append(job_dict)
    
    # Write to file
    output_path = Path(output_file)
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(jobs_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Backed up {len(jobs_data)} jobs to {output_file}")
    return output_file

async def get_migration_status(session: AsyncSession) -> Dict[str, Any]:
    """Get migration status and statistics"""
    repository = JobRepository(session)
    
    # Load categories from categories.yml
    from ..categories import CategoryManager
    category_manager = CategoryManager()
    categories = category_manager.get_enabled_category_names()
    
    stats = {}
    
    for category in categories:
        jobs = await repository.get_jobs_by_category(category, days_limit=0)
        recent_jobs = await repository.get_jobs_by_category(category, days_limit=30)
        unsent_jobs = await repository.get_jobs_by_category(category, days_limit=30, only_unsent=True)
        
        stats[category] = {
            "total_jobs": len(jobs),
            "recent_jobs_30_days": len(recent_jobs),
            "unsent_jobs": len(unsent_jobs),
            "latest_job_date": jobs[0].date_posted.strftime("%d/%m/%Y") if jobs else "No jobs"
        }
    
    # Overall stats
    overall_stats = await repository.get_job_stats(30)
    stats["overall"] = overall_stats
    
    return stats

def print_migration_status(stats: Dict[str, Any]):
    """Print migration status in a readable format"""
    print("\n" + "="*50)
    print("📊 DATABASE MIGRATION STATUS")
    print("="*50)
    
    # Separate categories with jobs from empty ones
    active_categories = []
    empty_categories = []
    
    for category, data in stats.items():
        if category == "overall":
            continue
        
        if data['total_jobs'] > 0:
            active_categories.append((category, data))
        else:
            empty_categories.append(category)
    
    # Show active categories
    if active_categories:
        print(f"\n🟢 ACTIVE CATEGORIES ({len(active_categories)} with jobs)")
        for category, data in active_categories:
            print(f"\n🏷️ {category.upper()}")
            print(f"   Total jobs: {data['total_jobs']}")
            print(f"   Recent (30 days): {data['recent_jobs_30_days']}")
            print(f"   Unsent jobs: {data['unsent_jobs']}")
            print(f"   Latest job: {data['latest_job_date']}")
    
    # Show summary of empty categories
    if empty_categories:
        print(f"\n⚪ EMPTY CATEGORIES ({len(empty_categories)} with no jobs)")
        print(f"   Categories: {', '.join(empty_categories[:10])}")
        if len(empty_categories) > 10:
            print(f"   ... and {len(empty_categories) - 10} more")
    
    # Overall stats
    if "overall" in stats:
        overall = stats["overall"]
        print(f"\n📈 OVERALL STATS (Last 30 days)")
        print(f"   Total categories: {len(active_categories) + len(empty_categories)}")
        print(f"   Active categories: {len(active_categories)}")
        print(f"   Total jobs: {overall['total_jobs']}")
        print(f"   Sent to Telegram: {overall['sent_jobs']}")
        print(f"   Pending: {overall['unsent_jobs']}")
    
    print("\n" + "="*50)
