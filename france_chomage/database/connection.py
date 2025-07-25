"""
Database connection and session management
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.engine import URL

def get_database_url() -> str:
    """Get database URL from environment variables"""
    db_url = os.getenv("DATABASE_URL")
    
    if db_url:
        # Railway provides postgres:// URLs, convert to async format
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif not db_url.startswith("postgresql+asyncpg://"):
            db_url = f"postgresql+asyncpg://{db_url}"
        return db_url
    
    # Build URL from individual components
    return URL.create(
        "postgresql+asyncpg",
        username=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "france_chomage"),
    ).render_as_string(hide_password=False)

def create_engine():
    """Create async SQLAlchemy engine"""
    database_url = get_database_url()
    return create_async_engine(
        database_url,
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
        pool_pre_ping=False,    # Disabled to avoid event loop conflicts
        pool_recycle=1800,      # Recycle connections every 30 minutes
        pool_size=10,           # Increased pool size for concurrent operations
        max_overflow=20,        # Increased overflow for peak loads
        pool_timeout=60,        # Increased timeout for busy periods
        # Additional connection stability settings
        connect_args={
            "server_settings": {
                "application_name": "france_chomage_bot",
                "jit": "off",
            }
        }
    )

# Global engine and session factory (will be initialized later)
engine = None
async_session_factory = None

def initialize_database(force_reinit: bool = False):
    """Initialize database engine and session factory"""
    global engine, async_session_factory
    
    if engine is None or force_reinit:
        if engine is not None:
            # Clean up existing engine
            try:
                engine.dispose()
            except Exception:
                pass  # Ignore disposal errors
        
        engine = create_engine()
        async_session_factory = async_sessionmaker(
            engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        print(f"🔧 Database initialized with pool size: {engine.pool.size()}")

def get_connection_info():
    """Get current connection pool information"""
    if engine is None:
        return "Database not initialized"
    
    pool = engine.pool
    return f"Pool size: {pool.size()}, Checked out: {pool.checkedout()}, Overflow: {pool.overflow()}"

async def get_session() -> AsyncSession:
    """Get async database session"""
    # Ensure database is initialized
    if async_session_factory is None:
        initialize_database()
    
    return async_session_factory()
