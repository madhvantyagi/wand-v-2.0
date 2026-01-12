"""
Database connection and session management.
Supports SQLite (development) and PostgreSQL (AWS RDS production).
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Database URL - defaults to SQLite for development
# For AWS RDS PostgreSQL, set DATABASE_URL environment variable:
# DATABASE_URL=postgresql+asyncpg://user:password@endpoint:5432/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./wand.db"
)

# Detect database type
IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# Create async engine with appropriate settings
if IS_POSTGRES:
    # PostgreSQL / AWS RDS configuration
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=5,           # Connection pool size
        max_overflow=10,       # Extra connections if pool exhausted
        pool_timeout=30,       # Timeout for getting connection
        pool_recycle=1800,     # Recycle connections after 30 min
        pool_pre_ping=True,    # Verify connections are alive
    )
else:
    # SQLite for local development
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )

# Session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency for getting database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

