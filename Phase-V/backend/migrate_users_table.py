#!/usr/bin/env python3
"""
Migration script to add missing columns to users table.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from sqlmodel import create_engine, Session
from sqlalchemy import text


async def migrate_users_table():
    """
    Add missing columns to the users table.
    """
    # Import settings after path is set
    from src.config import settings
    
    # Create sync engine for migrations
    database_url = settings.database_url
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    sync_engine = create_engine(database_url)

    with Session(sync_engine) as session:
        # Add all missing columns in a single transaction
        migrations = [
            # updated_at
            ("ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW();", "updated_at"),
            # last_login_at
            ("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITHOUT TIME ZONE;", "last_login_at"),
            # is_active
            ("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;", "is_active"),
            # consent_granted_at
            ("ALTER TABLE users ADD COLUMN IF NOT EXISTS consent_granted_at TIMESTAMP WITHOUT TIME ZONE;", "consent_granted_at"),
            # consent_version
            ("ALTER TABLE users ADD COLUMN IF NOT EXISTS consent_version VARCHAR(20);", "consent_version"),
            # data_deletion_requested
            ("ALTER TABLE users ADD COLUMN IF NOT EXISTS data_deletion_requested BOOLEAN DEFAULT FALSE;", "data_deletion_requested"),
            # data_deletion_requested_at
            ("ALTER TABLE users ADD COLUMN IF NOT EXISTS data_deletion_requested_at TIMESTAMP WITHOUT TIME ZONE;", "data_deletion_requested_at"),
        ]

        for sql, column_name in migrations:
            try:
                session.execute(text(sql))
                print(f"[OK] Column '{column_name}' added or already exists")
            except Exception as e:
                print(f"[ERROR] Error adding column '{column_name}': {e}")
        
        session.commit()
        print("\n[SUCCESS] Users table migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(migrate_users_table())
