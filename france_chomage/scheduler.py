"""
Configuration-driven scheduler for the France Chômage bot
"""
import asyncio
import schedule
import time
from typing import Dict, Any
from france_chomage.config import settings
from france_chomage.categories import category_manager, CategoryConfig
from france_chomage.scraping.category_scraper import create_category_scraper
from france_chomage.telegram.bot import telegram_bot
from france_chomage.database.connection import initialize_database

# Global job statistics
job_stats: Dict[str, Dict[str, Any]] = {}


async def run_category_job(category_name: str) -> None:
    """Generic job runner for any category"""
    try:
        # Get category configuration
        category_config = category_manager.get_category(category_name)
        
        print(f"🎯 Starting {category_name} jobs...")
        print(f"🔍 Search terms: {category_config.search_terms}")
        print(f"📡 Topic ID: {category_config.telegram_topic_id}")
        
        # Create and run scraper
        print(f"📡 Scraping {category_name} in progress...")
        scraper = create_category_scraper(category_config)
        jobs = await scraper.scrape()
        
        print(f"📦 {len(jobs)} {category_name} jobs scraped")
        
        # Send to Telegram
        print(f"📤 Sending to Telegram...")
        sent_count = await telegram_bot.send_jobs_from_database(
            category=category_name,
            topic_id=category_config.telegram_topic_id
        )
        
        print(f"✅ {sent_count} new {category_name} jobs sent")
        
        # Save statistics
        job_stats[category_name] = {'jobs_sent': sent_count}
        
    except Exception as e:
        print(f"❌ Error in {category_name}: {e}")
        job_stats[category_name] = {'jobs_sent': 0, 'error': str(e)}


async def send_update_summary() -> None:
    """Send summary of job statistics to general topic"""
    if job_stats:
        print("📊 Sending update summary...")
        await telegram_bot.send_update_summary(job_stats)
        # Clear stats after sending
        job_stats.clear()


def create_sync_wrapper(category_name: str):
    """Create a synchronous wrapper for async category job"""
    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Reset database connection for this loop
            from france_chomage.database import connection
            connection.engine = None
            connection.async_session_factory = None
            loop.run_until_complete(run_category_job(category_name))
        finally:
            loop.close()
    
    return sync_wrapper


def sync_update_summary():
    """Synchronous wrapper for update summary"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Reset database connection for this loop
        from france_chomage.database import connection
        connection.engine = None
        connection.async_session_factory = None
        loop.run_until_complete(send_update_summary())
    finally:
        loop.close()


def schedule_categories() -> None:
    """Schedule all enabled categories based on configuration"""
    try:
        enabled_categories = category_manager.get_enabled_categories()
        
        if not enabled_categories:
            print("⚠️ No enabled categories found!")
            return
        
        print("📅 Scheduling categories:")
        
        # Schedule each category
        for name, config in enabled_categories.items():
            schedule_time = f"{config.schedule_hour:02d}:00"
            sync_wrapper = create_sync_wrapper(name)
            
            schedule.every().day.at(schedule_time).do(sync_wrapper).tag(name)
            print(f"   {config.name}: {schedule_time}")
            
            # Schedule update summary 5 minutes after each job
            summary_time = f"{config.schedule_hour:02d}:05"
            schedule.every().day.at(summary_time).do(sync_update_summary).tag('summary')
        
        print(f"✅ {len(enabled_categories)} categories scheduled")
        
    except Exception as e:
        print(f"❌ Error scheduling categories: {e}")
        raise


def run_startup_jobs() -> None:
    """Run all enabled categories once at startup"""
    if settings.skip_init_job:
        print("⏭️ Startup jobs skipped (SKIP_INIT_JOB=1)")
        return
    
    try:
        enabled_categories = category_manager.get_enabled_categories()
        print(f"\n🚀 Running startup jobs for {len(enabled_categories)} categories...")
        
        for name in enabled_categories.keys():
            print(f"\n--- Running {name} ---")
            sync_wrapper = create_sync_wrapper(name)
            sync_wrapper()
        
        print("\n✅ All startup jobs completed")
        
    except Exception as e:
        print(f"❌ Error running startup jobs: {e}")


def main():
    """Main scheduler entry point"""
    print("🔧 Initializing France Chômage Scheduler...")
    
    # Initialize database
    initialize_database()
    
    # Load category configuration
    try:
        category_manager.load_categories()
    except Exception as e:
        print(f"❌ Failed to load categories: {e}")
        print("💡 Make sure categories.yml exists and is valid")
        return
    
    # Schedule all categories
    try:
        schedule_categories()
    except Exception as e:
        print(f"❌ Failed to schedule categories: {e}")
        return
    
    # Run startup jobs
    run_startup_jobs()
    
    print("\n⏰ Scheduler active. Press Ctrl+C to stop.")
    
    # Main scheduling loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped")
    except Exception as e:
        print(f"\n❌ Scheduler error: {e}")


if __name__ == "__main__":
    main()
