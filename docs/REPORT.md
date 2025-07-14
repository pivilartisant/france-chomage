# Job Scraping Logic Summary

## Overview
The bot uses a **base scraper architecture** with specialized scrapers for each job category, built on top of the `python-jobspy` library.

## Core Components

### 1. Base Scraper (`ScraperBase`)
- **Abstract base class** that handles common scraping logic
- **Async execution** with retry mechanisms and anti-detection strategies
- **Environment-aware** site selection (Docker vs Local)
- **Error handling** with fallback strategies

### 2. Job Categories
Each category inherits from `ScraperBase` and defines:
- **Communication**: `"communication"`
- **Design**: `"design graphique OR graphiste OR UI UX OR designer"`
- **Restauration**: `"restauration OR cuisinier OR chef OR serveur OR barman OR sommelier OR commis"`

### 3. Environment Detection
- **Local mode**: Uses both Indeed + LinkedIn (higher risk of blocks)
- **Docker mode**: LinkedIn only (more stable)
- **Auto-detection** via `/.dockerenv`, `/proc/1/cgroup`, or env variables

## Scraping Process

### 1. Site Strategy
```python
# Environment-based site selection
Local: ["indeed", "linkedin"]    # All sites
Docker: ["linkedin"]             # LinkedIn only for stability
```

### 2. Anti-Detection Features
- **Random delays**: 2-8 seconds between requests
- **Extended delays for Indeed**: 5-15 seconds after failures
- **Result limits**: Max 10 results for Indeed to avoid detection
- **User-agent rotation**: Handled by jobspy library

### 3. Retry Logic
- **Max 3 attempts** per scraping session
- **Exponential backoff**: Increasing delays between retries
- **Automatic fallback**: If Indeed fails → try LinkedIn only
- **Error categorization**: 403 blocks, timeouts, connection issues

### 4. Data Processing
- **Pandas DataFrame** → **Pydantic Job models**
- **Data cleaning**: Removes NaN values, formats dates
- **Validation**: Field validation and sanitization
- **Persistence**: Saves to `jobs_{category}.json`

## Job Model
```python
class Job(BaseModel):
    # Required fields
    title: str
    company: str
    location: str
    date_posted: str
    job_url: str
    site: str
    
    # Optional fields
    salary_source: Optional[str]
    description: Optional[str]
    is_remote: bool = False
    job_type: Optional[str]
    company_industry: Optional[str]
    experience_range: Optional[str]
```

## Error Handling
- **403 Blocks**: Automatic LinkedIn-only fallback
- **Timeouts**: Increased delays and retry
- **Connection issues**: Network problem detection
- **Empty results**: Creates empty JSON file for consistent workflow

The system prioritizes **stability over quantity**, using conservative request patterns and graceful degradation when sites block access.

## Potential Improvements

### 1. Performance Enhancements
- **Parallel scraping**: Run multiple category scrapers concurrently instead of sequentially
- **Caching mechanism**: Implement Redis/in-memory cache to avoid re-scraping recent jobs
- **Database storage**: Replace JSON files with SQLite/PostgreSQL for better data management
- **Incremental scraping**: Only fetch new jobs since last scrape timestamp

### 2. Anti-Detection Improvements
- **Advanced user-agent rotation**: Implement comprehensive browser fingerprinting
- **Proxy rotation**: Add proxy pool support for IP rotation
- **Session management**: Maintain cookies and session state between requests
- **Behavioral patterns**: Randomize scroll patterns, click timings, and navigation flows
- **Rate limiting per site**: Implement site-specific rate limits and quotas

### 3. Data Quality Enhancements
- **Duplicate detection**: Implement fuzzy matching to identify duplicate jobs across sites
- **Relevance scoring**: Add ML-based job relevance scoring for better filtering
- **Job categorization**: Improve automatic job category detection using NLP
- **Data enrichment**: Fetch additional company information, salary ranges, and reviews
- **Content validation**: Detect and filter spam or irrelevant job postings

### 4. Monitoring & Observability
- **Health checks**: Add comprehensive health monitoring for scrapers
- **Metrics collection**: Track success rates, response times, and error patterns
- **Alerting system**: Implement real-time alerts for scraping failures
- **Dashboard**: Create monitoring dashboard for scraping statistics
- **Logging improvements**: Add structured logging with correlation IDs

### 5. Configuration & Flexibility
- **Dynamic configuration**: Allow runtime configuration updates without restart
- **Site-specific settings**: Per-site configuration for delays, limits, and strategies
- **A/B testing**: Framework for testing different scraping strategies
- **Feature flags**: Toggle features and strategies without code changes
- **Multi-location support**: Extend to scrape jobs from multiple cities

### 6. Error Handling & Resilience
- **Circuit breaker pattern**: Automatically disable failing sites temporarily
- **Graceful degradation**: Fallback to cached results when all sites fail
- **Exponential backoff**: Implement smarter backoff strategies per error type
- **Dead letter queue**: Store failed jobs for manual review and retry
- **Health recovery**: Automatic recovery mechanisms for common failure scenarios

### 7. User Experience Improvements
- **Job formatting**: Better Telegram message formatting with rich text
- **Job filtering**: User-configurable filters for salary, location, experience
- **Job matching**: Personalized job recommendations based on user preferences
- **Analytics**: Job market insights and trends reporting
- **Subscription management**: Allow users to subscribe to specific job categories

### 8. Scalability & Architecture
- **Queue-based processing**: Implement job queues (Redis/RabbitMQ) for async processing
- **Microservices**: Split scraping logic into independent services
- **Load balancing**: Distribute scraping load across multiple instances
- **Resource optimization**: Better memory and CPU usage optimization
- **Containerization**: Improved Docker setup with multi-stage builds

### 9. Security & Compliance
- **Data privacy**: Implement data retention policies and GDPR compliance
- **API rate limiting**: Protect internal APIs from abuse
- **Secret management**: Use proper secret management (HashiCorp Vault, AWS Secrets)
- **Audit logging**: Track all data access and modifications
- **Input validation**: Comprehensive validation of all external data

### 10. Integration & Extensibility
- **Plugin system**: Allow easy addition of new job sites and scrapers
- **API endpoints**: Expose REST API for job data access
- **Webhook support**: Real-time job notifications via webhooks
- **Export formats**: Support multiple export formats (CSV, XML, RSS)
- **Third-party integrations**: Connect with job boards, ATS systems, and recruiters


#### Conclusion
i want to solely focus on user experience and data quality improvements in the next iterations. 

##### Data Storage
1. i want to improve how i store data that is scraped. you can use a databaselike PostgreSQL to store job data instead of JSON files. This will allow for better querying, indexing, and data integrity. 

2. consider implementing a caching layer to avoid re-scraping jobs that have already been processed recently.

3. Only send new jobs since last scrape timestamp

##### User Experience
1. I want to send jobs that have been posted in the last 30 days to the user. This will ensure that users receive fresh and relevant job postings without overwhelming them with outdated information. Implement a filtering mechanism based on the job posting date to achieve this.

2. Better Telegram message formatting with rich text -> just change the date to be formatted as "dd/mm/yyyy" for better readability.


##### Implementation Strategy
Keep things simple and focus on the user experience and data quality improvements.

**Do NOT change** the core scraping logic or architecture at this stage. The goal is to enhance the existing system without introducing unnecessary complexity.

##### Questions for Clarification

**Database Implementation:**
1. Should we maintain the existing JSON files as backup/fallback while transitioning to PostgreSQL? 
- NO
2. Do you want to migrate existing job data from JSON files to the database?
-  NO
3. What's your preference for the database schema? Should we normalize company information, locations, etc.?
-  best practice is to normalize the data for better integrity and querying.

**Date Filtering (30-day rule):**
1. Should the 30-day filter apply at scraping time or display time? 
   - Apply at scraping time to avoid sending outdated jobs.
2. Do you want to store older jobs in the database but only send recent ones to Telegram?
- Yes, store all jobs but filter out those older than 30 days when sending to Telegram.
3. How should we handle jobs with missing or invalid dates?
- Jobs with missing or invalid dates should be excluded from the 30-day filter and not sent to Telegram.

**Caching Strategy:**
1. Should we cache based on job URL, title+company combination, or both?
- Cache based on job URL to ensure uniqueness and prevent duplicates.
2. How long should the cache retention be (hours/days)?
- Retain cache for 24 hours to balance freshness and performance.
3. Should duplicate detection work across different job sites?
- No, focus on duplicates within the same site to avoid confusion.

**Message Formatting:**
1. Beyond date formatting (dd/mm/yyyy), any other formatting improvements needed?
- No additional formatting changes needed at this stage.
2. Should we maintain the current message structure or can we optimize it?
- Maintain the current structure but ensure the date is clearly formatted for readability.

##### Implementation Priority Order
Based on your requirements, suggest this order:

1. **Database migration** (PostgreSQL setup + data model)
2. **30-day date filtering** (filter jobs by posting date)
3. **Caching mechanism** (prevent duplicate job processing)
4. **Date formatting** (dd/mm/yyyy in Telegram messages)
5. **Incremental scraping** (only new jobs since last run)

##### Success Criteria
- Users receive only fresh, relevant jobs (≤30 days old)
- No duplicate jobs sent to Telegram
- Improved message readability with proper date formatting
- Faster scraping through caching and incremental updates
- Reliable data storage with PostgreSQL




