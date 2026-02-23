#!/usr/bin/env python3
"""
Migration script to add difficulty_level column to tasks table.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text


async def migrate_add_difficulty_level():
    """
    Add difficulty_level column to the tasks table.
    """
    # Import settings after path is set
    from src.config import settings
    
    # Create sync engine for migrations
    database_url = settings.database_url
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    sync_engine = create_engine(database_url)

    with Session(sync_engine) as session:
        # Add the difficulty_level column if it doesn't exist
        alter_table_sql = text("""
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS difficulty_level VARCHAR(20) DEFAULT 'intermediate';
        """)

        session.execute(alter_table_sql)
        session.commit()

        print("Successfully added difficulty_level column to tasks table")


if __name__ == "__main__":
    asyncio.run(migrate_add_difficulty_level())