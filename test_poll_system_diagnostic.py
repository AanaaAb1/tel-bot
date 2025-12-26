#!/usr/bin/env python3
"""
Poll System Diagnostic Test

This test simulates the complete poll-based question flow to identify why 
next questions don't appear after users answer questions.
"""

import sys
import os
import logging
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, Poll, PollAnswer
from telegram.ext import Application, CallbackContext, PollAnswerHandler

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the handlers
from app.handlers.radio_question_handler_poll import (
    handle_poll_answer,
    show_next_question,
    start_exam_with_polls,
    create_poll_question
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mock_poll_answer(poll_id, option_ids, user_id=12345):
    """Create a mock poll answer"""
    poll_answer = Mock()
    poll_answer.poll_id = poll_id
    poll_answer.option_ids = option_ids
    poll_answer.user = Mock()
    poll_answer.user.id = user_id
    return poll_answer

def create_mock_poll(poll_id, question_id=1):
    """Create a mock poll"""
    poll = Mock()
    poll.id = poll_id
    poll.question = "Test Question"
    poll.options = [Mock(), Mock()]
    poll.correct_option_id = 0
    return poll

def create_mock_update_with_poll_answer(poll_id, option_ids, user_id=12345):
    """Create a mock update with poll answer"""
    update = Mock()
    update.poll_answer = create_mock_poll_answer(poll_id, option_ids, user_id)
    update.effective_user = Mock()
    update.effective_user.id = user_id
    update.effective_chat = Mock()
    update.effective_chat.id = user_id
    return update

def create_mock_context(user_data):
    """Create a mock context with user data"""
    context = Mock()
    context.user_data = user_data
    context.bot = Mock()
    context.bot.send_poll = AsyncMock()
    context.bot.send_message = AsyncMock()
    return context

async def test_poll_answer_flow():
    """Test the complete poll answer flow"""
    print("\n🧪 Testing Poll Answer Flow...")
    
    # Step 1: Initialize user data as practice handler would
    user_data = {
        "user_id": 12345,
        "chat_id": 12345,
        "questions": [
            Mock(id=1, text="Question 1", option_a="A1", option_b="B1", correct_answer="A"),
            Mock(id=2, text="Question 2", option_a="A2", option_b="B2", correct_answer="B"),
            Mock(id=3, text="Question 3", option_a="A3", option_b="B3", correct_answer="A")
        ],
        "index": 0,
        "practice_mode": True,
        "use_timer": False,
        "chapter_completion": True,
        "current_poll_id": "test_poll_123"
    }
    
    # Step 2: Create mock context
    context = create_mock_context(user_data)
    
    # Step 3: Create mock update with poll answer
    update = create_mock_update_with_poll_answer("test_poll_123", [0])  # Select option A (0)
    
    print(f"  📊 Initial state:")
    print(f"    - Current question index: {user_data['index']}")
    print(f"    - Total questions: {len(user_data['questions'])}")
    print(f"    - Current poll ID: {user_data.get('current_poll_id')}")
    
    try:
        # Step 4: Call handle_poll_answer
        print("\n  📤 Calling handle_poll_answer...")
        await handle_poll_answer(update, context)
        
        print(f"\n  📊 After handling answer:")
        print(f"    - Question index: {user_data['index']}")
        print(f"    - Next question exists: {user_data['index'] < len(user_data['questions'])}")
        
        # Step 5: Check if show_next_question was called
        if context.bot.send_poll.called:
            call_args = context.bot.send_poll.call_args
            print(f"  ✅ show_next_question called successfully")
            print(f"    - Chat ID: {call_args.kwargs.get('chat_id')}")
            print(f"    - Question: {call_args.kwargs.get('question', '')[:50]}...")
        else:
            print(f"  ❌ show_next_question was NOT called")
            return False
            
        # Step 6: Test second question answer
        print(f"\n  🔄 Testing second question answer...")
        user_data["index"] = 1
        user_data["current_poll_id"] = "test_poll_456"
        
        update2 = create_mock_update_with_poll_answer("test_poll_456", [1])  # Select option B (1)
        context2 = create_mock_context(user_data)
        
        await handle_poll_answer(update2, context2)
        
        print(f"  📊 After second answer:")
        print(f"    - Question index: {user_data['index']}")
        print(f"    - Should show completion: {user_data['index'] >= len(user_data['questions'])}")
        
        if context2.bot.send_message.called:
            print(f"  ✅ Completion message called")
            print(f"    - Chat ID: {context2.bot.send_message.call_args.kwargs.get('chat_id')}")
        else:
            print(f"  ❌ Completion message NOT called")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_poll_question_creation():
    """Test poll question creation"""
    print("\n🧪 Testing Poll Question Creation...")
    
    question = Mock(
        id=1,
        text="What is the capital of France?",
        option_a="London",
        option_b="Berlin", 
        option_c="Paris",
        option_d="Madrid",
        correct_answer="C"
    )
    
    try:
        poll_data = create_poll_question(question, 1, 5)
        
        print(f"  📝 Question: {poll_data['question']}")
        print(f"  🔘 Options: {poll_data['options']}")
        print(f"  ✅ Correct option ID: {poll_data['correct_option_id']}")
        
        # Check if correct answer is Paris (index 2)
        if poll_data['correct_option_id'] == 2:
            print(f"  ✅ Correct answer mapping works")
            return True
        else:
            print(f"  ❌ Correct answer mapping failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Poll creation failed: {e}")
        return False

async def test_user_data_validation():
    """Test user data validation for poll system"""
    print("\n🧪 Testing User Data Validation...")
    
    test_cases = [
        {
            "name": "Valid practice data",
            "data": {
                "user_id": 12345,
                "chat_id": 12345,
                "questions": [Mock()],
                "index": 0,
                "practice_mode": True,
                "current_poll_id": "test_123"
            },
            "should_pass": True
        },
        {
            "name": "Missing current_poll_id",
            "data": {
                "user_id": 12345,
                "chat_id": 12345,
                "questions": [Mock()],
                "index": 0,
                "practice_mode": True
            },
            "should_pass": False
        },
        {
            "name": "Wrong poll_id",
            "data": {
                "user_id": 12345,
                "chat_id": 12345,
                "questions": [Mock()],
                "index": 0,
                "practice_mode": True,
                "current_poll_id": "different_123"
            },
            "should_pass": False
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\n  🔍 Testing: {test_case['name']}")
        user_data = test_case["data"]
        context = create_mock_context(user_data)
        update = create_mock_update_with_poll_answer("test_123", [0])
        
        try:
            await handle_poll_answer(update, context)
            if test_case["should_pass"]:
                print(f"    ✅ Passed as expected")
                results.append(True)
            else:
                print(f"    ❌ Should have failed but passed")
                results.append(False)
        except Exception as e:
            if test_case["should_pass"]:
                print(f"    ❌ Should have passed but failed: {e}")
                results.append(False)
            else:
                print(f"    ✅ Failed as expected")
                results.append(True)
    
    return all(results)

async def main():
    """Run all diagnostic tests"""
    print("🔍 POLL SYSTEM DIAGNOSTIC TEST")
    print("=" * 60)
    
    tests = [
        ("Poll Question Creation", test_poll_question_creation()),
        ("User Data Validation", test_user_data_validation()),
        ("Complete Poll Answer Flow", test_poll_answer_flow())
    ]
    
    results = []
    for test_name, test_coro in tests:
        try:
            result = await test_coro
            results.append(result)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n{test_name}: ❌ ERROR - {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed - Poll system should work correctly")
        print("If next questions still don't appear, the issue might be:")
        print("  • PollAnswerHandler not registered in dispatcher")
        print("  • Telegram API issues with poll creation")
        print("  • Bot permissions for poll functionality")
    else:
        print(f"\n❌ {total - passed} test(s) failed - Issues found:")
        print("  • Poll system configuration problems")
        print("  • Handler registration issues")
        print("  • User data flow problems")
    
    return passed == total

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

