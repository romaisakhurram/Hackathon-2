#!/usr/bin/env python3
"""
Test the intent recognizer with simple pattern matching
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

async def test_intent():
    from src.ai_agent.intent_recognizer import IntentRecognizer
    
    recognizer = IntentRecognizer()
    
    test_inputs = [
        "add a task to buy a car",
        "Add the task description buy a car",
        "create a new task",
        "list my tasks",
        "show tasks"
    ]
    
    for user_input in test_inputs:
        result = await recognizer.recognize_intent(user_input)
        print(f"\nInput: {user_input}")
        print(f"Intent: {result.intent_type.value}")
        print(f"Confidence: {result.confidence}")
        print(f"Parameters: {result.parameters}")

if __name__ == "__main__":
    asyncio.run(test_intent())
