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


async def run_scrape_job(category_name: str) -> None:
    """Run scraping job for a category"""
    try:
        # Get category configuration
        category_config = category_manager.get_category(category_name)
        
        print(f"🎯 Starting scraping for {category_name}...")
        print(f"🔍 Search terms: {category_config.search_terms}")
        
        # Create and run scraper
        print(f"📡 Scraping {category_name} in progress...")
        scraper = create_category_scraper(category_config)
        jobs = await scraper.scrape()
        
        print(f"📦 {len(jobs)} {category_name} jobs scraped and saved to database")
        
        # Save statistics for scraping
        if category_name not in job_stats:
            job_stats[category_name] = {}
        job_stats[category_name]['jobs_scraped'] = len(jobs)
        
    except Exception as e:
        print(f"❌ Error scraping {category_name}: {e}")
        if category_name not in job_stats:
            job_stats[category_name] = {}
        job_stats[category_name]['scrape_error'] = str(e)


async def run_send_job(category_name: str) -> None:
    """Run sending job for a category"""
    try:
        # Get category configuration
        category_config = category_manager.get_category(category_name)
        
        print(f"🎯 Starting sending for {category_name}...")
        print(f"📡 Topic ID: {category_config.telegram_topic_id}")
        
        # Send to Telegram
        print(f"📤 Sending to Telegram...")
        sent_count = await telegram_bot.send_jobs_from_database(
            category=category_name,
            topic_id=category_config.telegram_topic_id
        )
        
        print(f"✅ {sent_count} new {category_name} jobs sent")
        
        # Save statistics for sending
        if category_name not in job_stats:
            job_stats[category_name] = {}
        job_stats[category_name]['jobs_sent'] = sent_count
        
    except Exception as e:
        print(f"❌ Error sending {category_name}: {e}")
        if category_name not in job_stats:
            job_stats[category_name] = {}
        job_stats[category_name]['send_error'] = str(e)


async def run_category_job(category_name: str) -> None:
    """Legacy combined job runner for backward compatibility"""
    print(f"⚠️ Using legacy combined job runner for {category_name}")
    print("💡 Consider using separate scrape and send jobs for better reliability")
    
    await run_scrape_job(category_name)
    await run_send_job(category_name)


async def send_update_summary() -> None:
    """Send summary of job statistics to general topic"""
    if job_stats:
        print("📊 Sending update summary...")
        await telegram_bot.send_update_summary(job_stats)
        # Clear stats after sending
        job_stats.clear()


def create_sync_wrapper(category_name: str, job_type: str = 'combined'):
    """Create a synchronous wrapper for async category job"""
    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Initialize database connection for this loop
            from france_chomage.database import connection
            connection.initialize_database()
            
            if job_type == 'scrape':
                loop.run_until_complete(run_scrape_job(category_name))
            elif job_type == 'send':
                loop.run_until_complete(run_send_job(category_name))
            else:
                # Legacy combined job
                loop.run_until_complete(run_category_job(category_name))
        finally:
            loop.close()
    
    return sync_wrapper


def sync_update_summary():
    """Synchronous wrapper for update summary"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Initialize database connection for this loop
        from france_chomage.database import connection
        connection.initialize_database()
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
        
        print("📅 Scheduling categories with separate scrape and send jobs:")
        
        # Schedule each category with separate scrape and send jobs
        for name, config in enabled_categories.items():
            # Schedule scraping jobs
            for scrape_hour in config.scrape_hours:
                scrape_time = f"{scrape_hour:02d}:00"
                scrape_wrapper = create_sync_wrapper(name, 'scrape')
                schedule.every().day.at(scrape_time).do(scrape_wrapper).tag(f'{name}_scrape')
            
            # Schedule sending jobs
            for send_hour in config.send_hours:
                send_time = f"{send_hour:02d}:00"
                send_wrapper = create_sync_wrapper(name, 'send')
                schedule.every().day.at(send_time).do(send_wrapper).tag(f'{name}_send')
        
        # Schedule update summary once per day at 23:59
        schedule.every().day.at("23:59").do(sync_update_summary).tag('summary')
        
        print(f"✅ {len(enabled_categories)} categories scheduled with separate jobs")
        
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
        print("📝 Using separate scrape and send operations...")
        
        # First, run all scraping jobs
        print("\n🔍 Phase 1: Scraping all categories...")
        for name in enabled_categories.keys():
            print(f"\n--- Scraping {name} ---")
            scrape_wrapper = create_sync_wrapper(name, 'scrape')
            scrape_wrapper()
        
        # Then, run all sending jobs
        print("\n📤 Phase 2: Sending all categories...")
        for name in enabled_categories.keys():
            print(f"\n--- Sending {name} ---")
            send_wrapper = create_sync_wrapper(name, 'send')
            send_wrapper()
        
        print("\n✅ All startup jobs completed (scrape + send separated)")
        
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
