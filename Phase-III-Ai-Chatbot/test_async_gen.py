#!/usr/bin/env python3
"""
Simple test to find async generator context manager error
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

async def test_imports():
    print("Testing imports...")
    
    try:
        from src.database import get_async_session
        print("✓ get_async_session imported")
    except Exception as e:
        print(f"✗ Error importing get_async_session: {e}")
    
    try:
        from src.utils.conversation_context_manager import get_conversation_context_manager
        print("✓ get_conversation_context_manager imported")
        mgr = get_conversation_context_manager()
        print(f"✓ get_conversation_context_manager() returns: {type(mgr)}")
    except Exception as e:
        print(f"✗ Error with conversation_context_manager: {e}")
    
    try:
        from src.services.conversation_service import ConversationService
        print("✓ ConversationService imported")
    except Exception as e:
        print(f"✗ Error importing ConversationService: {e}")
    
    try:
        from src.services.message_service import MessageService
        print("✓ MessageService imported")
    except Exception as e:
        print(f"✗ Error importing MessageService: {e}")

if __name__ == "__main__":
    asyncio.run(test_imports())
