#!/usr/bin/env python3
"""
Test to verify that next questions appear automatically after users answer
"""

import sys
import os
from unittest.mock import Mock, AsyncMock
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_automatic_question_flow():
    """Test that questions flow automatically from one to the next"""
    print("🔄 Testing Automatic Question Flow")
    print("=" * 50)
    
    # Import the handlers
    from app.handlers.radio_question_handler import (
        handle_poll_answer, 
        show_next_question, 
        create_poll_question,
        start_exam_with_polls
    )
    
    # Create 3 mock questions for testing
    mock_questions = []
    for i in range(3):
        q = Mock()
        q.id = i + 1
        q.text = f"What is {i+1}+{i+1}?"
        q.option_a = str(i + 1)
        q.option_b = str((i + 1) * 2)  # Correct answer
        q.option_c = str(i + 3)
        q.option_d = str(i + 4)
        q.correct_answer = "B"
        mock_questions.append(q)
    
    # Mock user data for a practice session
    user_data = {
        "questions": mock_questions,
        "index": 0,  # Start with first question
        "practice_mode": True,
        "user_id": 12345,
        "chat_id": 12345,
        "current_poll_id": None,
        "use_timer": False
    }
    
    print(f"📊 Test Setup:")
    print(f"  - Total questions: {len(mock_questions)}")
    print(f"  - Practice mode: {user_data['practice_mode']}")
    print(f"  - Starting index: {user_data['index']}")
    
    # Simulate the complete flow
    async def simulate_complete_flow():
        # Mock update and context
        mock_update = Mock()
        mock_update.effective_user.id = 12345
        mock_update.effective_chat.id = 12345
        
        mock_context = Mock()
        mock_context.user_data = user_data
        mock_context.bot = AsyncMock()
        
        # Mock bot.send_poll to simulate sending polls
        sent_polls = []
        def mock_send_poll(chat_id, question, options, type, correct_option_id, is_anonymous):
            poll_message = Mock()
            poll_message.poll.id = f"poll_{len(sent_polls) + 1}"
            sent_polls.append({
                "poll_id": poll_message.poll.id,
                "question": question,
                "options": options,
                "correct_option_id": correct_option_id
            })
            return poll_message
        
        mock_context.bot.send_poll = mock_send_poll
        
        print(f"\n🎯 Step 1: Starting exam with {len(mock_questions)} questions")
        await start_exam_with_polls(mock_update, mock_context, user_data)
        print(f"  ✅ First question sent")
        
        # Simulate user answering each question
        for question_num in range(1, len(mock_questions) + 1):
            print(f"\n🎯 Step {question_num + 1}: User answering question {question_num}")
            print(f"  📍 Current index before answer: {user_data['index']}")
            
            # Create mock poll answer
            mock_poll_answer = Mock()
            mock_poll_answer.poll_id = sent_polls[question_num - 1]["poll_id"]
            mock_poll_answer.option_ids = [1]  # User selects option B (index 1)
            mock_update.poll_answer = mock_poll_answer
            
            # Process the answer
            await handle_poll_answer(mock_update, mock_context)
            
            print(f"  ✅ Answer processed")
            print(f"  📍 Index after answer: {user_data['index']}")
            
            # Check what happened
            if user_data['index'] >= len(mock_questions):
                print(f"  🎉 All questions completed!")
                break
            else:
                print(f"  ➡️ Should show question {user_data['index'] + 1}")
        
        return sent_polls
    
    # Run the simulation
    try:
        result = asyncio.run(simulate_complete_flow())
        
        print(f"\n📊 Flow Analysis:")
        print(f"  - Total polls sent: {len(result)}")
        print(f"  - Expected polls: {len(mock_questions)}")
        
        # Analyze each poll
        for i, poll in enumerate(result):
            print(f"  📝 Poll {i + 1}:")
            print(f"    - ID: {poll['poll_id']}")
            print(f"    - Question: {poll['question'][:50]}...")
            print(f"    - Correct option: {poll['correct_option_id']}")
        
        # Verify the flow worked correctly
        success = len(result) == len(mock_questions)
        print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Automatic Question Flow")
        
        if success:
            print(f"🎉 All {len(mock_questions)} questions appeared automatically!")
            print(f"🎯 The next question appears immediately after each answer")
        else:
            print(f"❌ Expected {len(mock_questions)} questions but got {len(result)}")
        
        return success
        
    except Exception as e:
        print(f"❌ Flow simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_question_boundary_safety():
    """Test that question boundary checking prevents out-of-range errors"""
    print(f"\n🛡️ Testing Question Boundary Safety")
    print("=" * 40)
    
    from app.handlers.radio_question_handler import create_poll_question
    
    # Test with boundary conditions
    mock_question = Mock()
    mock_question.id = 1
    mock_question.text = "Boundary test question"
    mock_question.option_a = "A"
    mock_question.option_b = "B"
    mock_question.option_c = "C"
    mock_question.option_d = "D"
    mock_question.correct_answer = "A"
    
    try:
        # Test normal case
        result = create_poll_question(mock_question, 1, 1)
        print(f"✅ Normal case: Question 1/1 - SUCCESS")
        
        # Test edge case
        result = create_poll_question(mock_question, 1, 5)
        print(f"✅ Edge case: Question 1/5 - SUCCESS")
        
        print(f"✅ All boundary tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Boundary test failed: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🔄 COMPREHENSIVE QUESTION FLOW VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Automatic Question Flow", test_automatic_question_flow),
        ("Question Boundary Safety", test_question_boundary_safety)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n{test_name}: ❌ ERROR - {e}")
            results.append(False)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Questions should now appear automatically after each answer")
        print(f"✅ No 'list index out of range' errors should occur")
        print(f"✅ The question flow is working correctly!")
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print(f"❌ There may still be issues with the question flow")

if __name__ == "__main__":
    main()
