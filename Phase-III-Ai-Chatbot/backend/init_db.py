"""
Database initialization script for Todo app.
This script creates the necessary tables in the database.
"""

import asyncio
import sys
import os
import urllib.parse

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from src.models.task import Task
from src.models.user import User
from src.config import settings


async def create_tables():
    """Create all database tables."""
    print("Connecting to database...")
    print(f"Database URL: {settings.database_url[:50]}...")  # Show first 50 chars

    # Use the database URL directly since we've already removed unsupported parameters
    database_url = settings.database_url

    # Convert to asyncpg format if it's postgresql
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"Using cleaned URL: {database_url[:50]}...")  # Show first 50 chars

    # Create engine with the cleaned URL
    engine = create_async_engine(
        database_url,
        echo=True,  # Enable echo to see what's happening
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
    )

    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    print("Tables created successfully!")

    # Close the engine
    await engine.dispose()

    print("\nTables created:")
    for table in SQLModel.metadata.tables.values():
        print(f"- {table.name}")


if __name__ == "__main__":
    print("Starting database initialization...")
    try:
        asyncio.run(create_tables())
        print("Database initialization completed successfully!")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        sys.exit(1)