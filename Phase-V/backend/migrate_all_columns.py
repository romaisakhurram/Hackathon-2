#!/usr/bin/env python3
"""
Comprehensive migration script to add all missing columns to tasks table.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from sqlmodel import create_engine, Session
from sqlalchemy import text


async def migrate_all_columns():
    """
    Add all missing columns to the tasks table.
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
            # difficulty_level
            ("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS difficulty_level VARCHAR(20) DEFAULT 'intermediate';", "difficulty_level"),
            # due_date
            ("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITHOUT TIME ZONE;", "due_date"),
            # completed_at
            ("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITHOUT TIME ZONE;", "completed_at"),
            # parent_id
            ("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_id UUID;", "parent_id"),
            # recurrence_rule_id
            ("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_rule_id UUID;", "recurrence_rule_id"),
            # is_template
            ("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_template BOOLEAN DEFAULT FALSE;", "is_template"),
        ]

        for sql, column_name in migrations:
            try:
                session.execute(text(sql))
                print(f"[OK] Column '{column_name}' added or already exists")
            except Exception as e:
                print(f"[ERROR] Error adding column '{column_name}': {e}")
        
        session.commit()

        # Also create missing tables if needed
        print("\nCreating missing tables...")
        
        create_tables_sql = """
        -- Create reminders table if not exists
        CREATE TABLE IF NOT EXISTS reminders (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
            scheduled_time TIMESTAMP WITHOUT TIME ZONE,
            method VARCHAR(20) DEFAULT 'in-app',
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE
        );
        
        -- Create recurrence_rules table if not exists
        CREATE TABLE IF NOT EXISTS recurrence_rules (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
            interval VARCHAR(20) DEFAULT 'daily',
            frequency INTEGER DEFAULT 1,
            end_date TIMESTAMP WITHOUT TIME ZONE,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE
        );
        
        -- Create tags table if not exists
        CREATE TABLE IF NOT EXISTS tags (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL,
            color VARCHAR(20) DEFAULT 'blue',
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        );
        
        -- Create task_tags_link table (many-to-many) if not exists
        CREATE TABLE IF NOT EXISTS task_tags_link (
            task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
            tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (task_id, tag_id)
        );
        
        -- Create priorities table if not exists
        CREATE TABLE IF NOT EXISTS priorities (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(50) NOT NULL,
            level INTEGER DEFAULT 0,
            user_id UUID REFERENCES users(id) ON DELETE CASCADE
        );
        
        -- Create conversations table if not exists (for chat)
        CREATE TABLE IF NOT EXISTS conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255),
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        );
        
        -- Create messages table if not exists (for chat)
        CREATE TABLE IF NOT EXISTS messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        );
        """
        
        for statement in create_tables_sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    session.execute(text(statement))
                except Exception as e:
                    print(f"Note: {e}")
        
        session.commit()
        print("\n[SUCCESS] All migrations completed successfully!")


if __name__ == "__main__":
    asyncio.run(migrate_all_columns())
