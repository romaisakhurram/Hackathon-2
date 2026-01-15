from sqlmodel import create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from sqlalchemy import text
from typing import AsyncGenerator
from contextlib import asynccontextmanager
import os
from .config import settings
import logging


# Set up logging
logger = logging.getLogger(__name__)

# Store the database URL to create engines when needed (lazy initialization)
DATABASE_URL = settings.database_url

# Engines will be initialized later during app startup
async_engine = None
sync_engine = None


def init_engines():
    """
    Initialize the database engines with the configured database URL.
    This is called during app startup to avoid import-time database connection attempts.
    """
    global async_engine, sync_engine

    print(f"DATABASE_URL: {DATABASE_URL[:50]}...")  # Debug: print first 50 chars of URL

    # Only initialize if engines haven't been set already
    if async_engine is not None and sync_engine is not None:
        print("Engines already initialized, skipping initialization")
        return

    # Determine if we should use PostgreSQL or fallback to SQLite
    if DATABASE_URL.startswith("postgresql"):
        print("Detected PostgreSQL URL, attempting to initialize engines...")
        # Try to use PostgreSQL with proper parameters for asyncpg
        try:
            # For asyncpg, we need to ensure the URL has the correct driver format
            # and remove unsupported parameters like sslmode and channel_binding
            async_db_url = DATABASE_URL
            if not DATABASE_URL.startswith("postgresql+asyncpg://"):
                # Convert standard PostgreSQL URL to asyncpg format
                async_db_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

            # Remove unsupported parameters for asyncpg
            if "sslmode=" in async_db_url or "channel_binding=" in async_db_url:
                # Parse and remove unsupported parameters
                import urllib.parse
                parsed = urllib.parse.urlparse(async_db_url)
                query_params = urllib.parse.parse_qs(parsed.query)

                # Remove unsupported parameters
                query_params.pop('sslmode', None)
                query_params.pop('channel_binding', None)

                # Reconstruct the query string
                new_query = urllib.parse.urlencode(query_params, doseq=True)
                async_db_url = urllib.parse.urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    new_query,
                    parsed.fragment
                ))

            print(f"Async DB URL: {async_db_url[:50]}...")  # Debug: print first 50 chars

            async_engine = create_async_engine(
                async_db_url,  # URL with asyncpg driver
                echo=False,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=300,  # Recycle connections every 5 minutes
            )
            print(f"Async engine created: {async_engine is not None}")

            # Sync engine for non-async operations if needed
            from sqlalchemy.pool import QueuePool  # Use standard QueuePool for sync engine
            sync_db_url = async_db_url.replace("postgresql+asyncpg://", "postgresql://")
            sync_engine = create_engine(
                sync_db_url,
                echo=False,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=300,
            )
            print(f"Sync engine created: {sync_engine is not None}")

            print("Using PostgreSQL database")
        except Exception as e:
            print(f"Warning: Could not initialize PostgreSQL engines: {str(e)}")
            print("Falling back to SQLite for development...")

            # Fallback to SQLite for development purposes
            from sqlalchemy.pool import StaticPool
            async_engine = create_async_engine(
                "sqlite+aiosqlite:///:memory:",
                echo=False,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False}
            )
            print(f"Async engine (fallback): {async_engine is not None}")

            sync_engine = create_engine(
                "sqlite:///./test.db",
                echo=False,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False}
            )
            print(f"Sync engine (fallback): {sync_engine is not None}")
    else:
        # Use SQLite for anything other than PostgreSQL
        from sqlalchemy.pool import StaticPool
        async_engine = create_async_engine(
            DATABASE_URL,  # Use the provided DATABASE_URL directly
            echo=False,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        print(f"Async engine (direct SQLite): {async_engine is not None}")

        sync_engine = create_engine(
            DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://"),
            echo=False,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        print(f"Sync engine (direct SQLite): {sync_engine is not None}")
        print("Using SQLite database")

    # Ensure engines are initialized even if there were exceptions
    if async_engine is None:
        print("Critical: Both engines are None, falling back to default SQLite")
        from sqlalchemy.pool import StaticPool
        async_engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        sync_engine = create_engine(
            "sqlite:///./test.db",
            echo=False,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
    else:
        print(f"Final async engine: {async_engine is not None}")
        print(f"Final sync engine: {sync_engine is not None}")


def get_engines():
    """
    Get the database engines, initializing them if they don't exist.
    """
    global async_engine, sync_engine

    if async_engine is None or sync_engine is None:
        init_engines()

    return async_engine, sync_engine


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session with graceful degradation (T045).
    """
    global async_engine

    # Initialize engine if not already done
    if async_engine is None:
        init_engines()

    try:
        async with AsyncSession(async_engine) as session:
            yield session
    except DisconnectionError:
        logger.error("Database disconnection error occurred")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}")
        # Log the error but don't expose internal details to the user
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database session: {str(e)}")
        raise


def get_sync_session() -> Session:
    """
    Get a sync database session with graceful degradation (T045).
    """
    global sync_engine

    # Initialize engine if not already done
    if sync_engine is None:
        init_engines()

    try:
        with Session(sync_engine) as session:
            yield session
    except DisconnectionError:
        logger.error("Database disconnection error occurred")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}")
        # Log the error but don't expose internal details to the user
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database session: {str(e)}")
        raise


async def check_database_connection() -> bool:
    """
    Check if the database connection is healthy.
    """
    global async_engine

    # Initialize engine if not already done
    if async_engine is None:
        init_engines()

    try:
        async with AsyncSession(async_engine) as session:
            # Try a simple query to test connection
            await session.exec(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False