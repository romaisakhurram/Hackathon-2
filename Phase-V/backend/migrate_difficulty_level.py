#!/usr/bin/env python3
"""
Migration script to add difficulty_level column to tasks table.
"""

import asyncio
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
from backend.src.models.task import Task
from backend.src.config import settings


async def migrate_add_difficulty_level():
    """
    Add difficulty_level column to the tasks table.
    """
    # Create sync engine for migrations
    sync_engine = create_engine(settings.database_url.replace("postgresql+asyncpg://", "postgresql://"))
    
    with Session(sync_engine) as session:
        # Add the difficulty_level column if it doesn't exist
        alter_table_sql = """
        ALTER TABLE tasks ADD COLUMN IF NOT EXISTS difficulty_level VARCHAR(20) DEFAULT 'intermediate';
        """
        
        session.exec(alter_table_sql)
        session.commit()
        
        print("Successfully added difficulty_level column to tasks table")


if __name__ == "__main__":
    asyncio.run(migrate_add_difficulty_level())