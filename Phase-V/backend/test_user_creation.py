#!/usr/bin/env python3
"""Test user creation"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.config import settings
from src.database import get_async_session
from src.models.user import User
from sqlmodel import select
import uuid
from datetime import datetime

async def test_user_creation():
    """Test creating a user"""
    async for session in get_async_session():
        try:
            # Check existing users
            statement = select(User)
            result = await session.execute(statement)
            users = result.scalars().all()
            print(f"Existing users: {len(users)}")
            for user in users:
                print(f"  - {user.email} ({user.name})")
            
            # Create new user
            user_id = uuid.uuid4()
            user = User(
                id=user_id,
                email="testuser@example.com",
                name="Test User",
                consent_granted_at=datetime.utcnow(),
                consent_version="1.0"
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print(f"\nUser created successfully!")
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Name: {user.name}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        break

if __name__ == "__main__":
    asyncio.run(test_user_creation())
