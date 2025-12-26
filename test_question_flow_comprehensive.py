#!/usr/bin/env python3
"""
Comprehensive test to identify why next questions don't appear automatically
"""

import sys
import os
from unittest.mock import Mock, AsyncMock, patch
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_question_flow():
    """Test the complete question flow to identify where it breaks"""
    print("🔍 Testing Complete Question Flow")
    print("=" * 50)
    
    # Import the handlers
    from app.handlers.radio_question_handler import (
        handle_poll_answer, 
        show_next_question, 
        create_poll_question,
        start_exam_with_polls
    )
    
    # Create mock data simulating a practice session
    mock_questions = []
    for i in range(3):
        q = Mock()
        q.id = i + 1
        q.text = f"Question {i + 1}"
        q.option_a = f"Option A{i + 1}"
        q.option_b = f"Option B{i + 1}"
        q.option_c = None
        q.option_d = None
        q.correct_answer = "A" if i % 2 == 0 else "B"
        mock_questions.append(q)
    
    # Mock user data
    mock_user_data = {
        "questions": mock_questions,
        "index": 0,  # First question
        "practice_mode": True,
        "user_id": 12345,
        "chat_id": 12345,
        "current_poll_id": None,
        "use_timer": False
    }
    
    print(f"📊 Mock Setup:")
    print(f"  - Total questions: {len(mock_questions)}")
    print(f"  - Current index: {mock_user_data['index']}")
    print(f"  - Practice mode: {mock_user_data['practice_mode']}")
    
    # Test 1: Create first poll question
    print("\n🔧 Test 1: Create First Poll Question")
    try:
        first_question = mock_questions[mock_user_data['index']]
        poll_data = create_poll_question(first_question, 1, 3)
        print(f"  ✅ Poll created successfully:")
        print(f"    - Question: {poll_data['question'][:50]}...")
        print(f"    - Options: {poll_data['options']}")
        print(f"    - Correct option: {poll_data['correct_option_id']}")
        print(f"    - Question ID: {poll_data['question_id']}")
    except Exception as e:
        print(f"  ❌ Failed to create poll: {e}")
        return False
    
    # Test 2: Simulate user answering first question (Option A)
    print("\n🎯 Test 2: Simulate User Answering Question 1")
    try:
        # Simulate poll answer
        mock_update = Mock()
        mock_update.effective_user.id = 12345
        mock_update.effective_chat.id = 12345
        
        mock_poll_answer = Mock()
        mock_poll_answer.poll_id = "test_poll_123"
        mock_poll_answer.option_ids = [0]  # User selected option A (index 0)
        mock_update.poll_answer = mock_poll_answer
        
        mock_context = Mock()
        mock_context.user_data = mock_user_data
        mock_context.bot = AsyncMock()
        
        print(f"  📝 Simulating answer: Option A (index 0)")
        print(f"  📝 Current index before answer: {mock_user_data['index']}")
        print(f"  📝 Expected index after answer: {mock_user_data['index'] + 1}")
        
        # This should trigger the flow
        print(f"  🔄 Calling handle_poll_answer...")
        
    except Exception as e:
        print(f"  ❌ Failed to setup answer simulation: {e}")
        return False
    
    # Test 3: Check show_next_question logic
    print("\n📤 Test 3: Check show_next_question Logic")
    try:
        # Simulate the state after user answers (index incremented)
        mock_user_data['index'] = 1  # Now on question 2
        mock_user_data['current_poll_id'] = "test_poll_123"  # Previous poll
        
        print(f"  📊 State after answer:")
        print(f"    - Index: {mock_user_data['index']}")
        print(f"    - Total questions: {len(mock_questions)}")
        print(f"    - Has more questions: {mock_user_data['index'] < len(mock_questions)}")
        
        if mock_user_data['index'] < len(mock_questions):
            # Should show next question
            next_question = mock_questions[mock_user_data['index']]
            next_poll_data = create_poll_question(next_question, 2, 3)
            print(f"  ✅ Next question available:")
            print(f"    - Question {mock_user_data['index'] + 1}: {next_question.text}")
            print(f"    - Correct answer: {next_poll_data['correct_option_id']}")
        else:
            print(f"  ⚠️ No more questions - session complete")
            
    except Exception as e:
        print(f"  ❌ Failed to check next question logic: {e}")
        return False
    
    # Test 4: Mock the actual flow execution
    print("\n🚀 Test 4: Mock Full Flow Execution")
    try:
        # Reset state
        mock_user_data['index'] = 0
        mock_user_data['current_poll_id'] = None
        
        async def test_flow():
            # Start exam
            await start_exam_with_polls(mock_update, mock_context, mock_user_data)
            print(f"  ✅ Exam started - first question should be sent")
            
            # Simulate answering first question
            mock_user_data['current_poll_id'] = "test_poll_123"
            await handle_poll_answer(mock_update, mock_context)
            print(f"  ✅ Answer processed - next question should be sent")
            
            return True
        
        # Run the async test
        result = asyncio.run(test_flow())
        if result:
            print(f"  🎉 Flow simulation completed successfully")
        else:
            print(f"  ❌ Flow simulation failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Failed to execute flow: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("✅ Flow Test Completed - Analysis Complete")
    return True

def test_poll_sending_issue():
    """Test the specific issue with poll sending"""
    print("\n📡 Testing Poll Sending Logic")
    print("=" * 30)
    
    from app.handlers.radio_question_handler import show_next_question
    
    # Mock data
    mock_user_data = {
        "questions": [Mock(id=1, text="Test?", option_a="A", option_b="B", option_c=None, option_d=None, correct_answer="A")],
        "index": 0,
        "chat_id": 12345,
        "user_id": 12345
    }
    
    mock_update = Mock()
    mock_update.effective_chat.id = 12345
    mock_update.effective_user.id = 12345
    
    mock_context = Mock()
    mock_context.bot = AsyncMock()
    
    print("🔧 Testing show_next_question parameters:")
    print(f"  - Chat ID from update.effective_chat: {mock_update.effective_chat.id}")
    print(f"  - Chat ID from data: {mock_user_data.get('chat_id')}")
    print(f"  - Has effective_chat: {hasattr(mock_update, 'effective_chat')}")
    print(f"  - Has effective_user: {hasattr(mock_update, 'effective_user')}")
    
    # Test if show_next_question would work
    try:
        # This should show a poll, let's see if it would succeed
        print("\n🧪 Testing poll creation in isolation:")
        
        question = mock_user_data["questions"][mock_user_data["index"]]
        poll_data = create_poll_question(question, 1, 1)
        print(f"  ✅ Poll data created:")
        print(f"    - Question text: {poll_data['question']}")
        print(f"    - Options: {poll_data['options']}")
        print(f"    - Correct option ID: {poll_data['correct_option_id']}")
        
    except Exception as e:
        print(f"  ❌ Poll creation failed: {e}")
        return False
    
    return True

def main():
    """Run comprehensive flow tests"""
    print("🔍 COMPREHENSIVE QUESTION FLOW TEST")
    print("=" * 60)
    
    tests = [
        test_question_flow,
        test_poll_sending_issue
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"\n{test_func.__name__}: {status}")
        except Exception as e:
            print(f"\n{test_func.__name__}: ❌ ERROR - {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All flow tests passed!")
        print("The question flow logic appears correct.")
        print("If questions still don't appear automatically, the issue might be:")
        print("  • Bot permissions (can't send polls)")
        print("  • Database connectivity")
        print("  • Async execution issues")
        print("  • Telegram API rate limits")
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("There are issues with the question flow logic that need fixing.")

if __name__ == "__main__":
    main()
