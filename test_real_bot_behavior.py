#!/usr/bin/env python3
"""
Real Bot Behavior Diagnostic Test

This test simulates the actual bot startup and practice flow to identify
why next questions aren't appearing after users answer.
"""

import sys
import os
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging to see what's happening
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_bot_startup():
    """Test if bot can start properly"""
    print("\n🚀 Testing Bot Startup...")
    
    try:
        # Test importing the dispatcher
        from app.bot.dispatcher_fixed import register_handlers
        print("  ✅ Dispatcher import successful")
        
        # Test importing practice handler
        from app.handlers.practice_handler import start_practice, practice_course_selected
        print("  ✅ Practice handler import successful")
        
        # Test importing radio question handler
        from app.handlers.radio_question_handler import (
            handle_poll_answer, 
            show_next_question, 
            start_exam_with_polls
        )
        print("  ✅ Radio question handler import successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Bot startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_practice_flow_simulation():
    """Simulate the complete practice flow"""
    print("\n📝 Testing Complete Practice Flow...")
    
    try:
        # Import handlers
        from app.handlers.practice_handler import practice_course_selected
        from app.handlers.radio_question_handler import start_exam_with_polls, handle_poll_answer
        
        # Create mock update and context
        update = Mock()
        update.callback_query = Mock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.data = "practice_course_1"
        update.callback_query.from_user = Mock()
        update.callback_query.from_user.id = 12345
        
        context = Mock()
        context.user_data = {}
        context.bot = Mock()
        context.bot.send_poll = AsyncMock()
        context.bot.send_message = AsyncMock()
        
        # Mock question data
        mock_questions = []
        for i in range(3):
            question = Mock()
            question.id = i + 1
            question.text = f"Test Question {i + 1}"
            question.option_a = f"Option A{i + 1}"
            question.option_b = f"Option B{i + 1}"
            question.option_c = None
            question.option_d = None
            question.correct_answer = "A" if i % 2 == 0 else "B"
            mock_questions.append(question)
        
        # Simulate practice course selection
        print("  📚 Simulating practice course selection...")
        
        # Mock the database and question service
        with patch('app.handlers.practice_handler.get_questions_by_course_name') as mock_get_questions:
            mock_get_questions.return_value = mock_questions
            
            # Set up user data as practice_course_selected would
            context.user_data["user_id"] = 12345
            context.user_data["chat_id"] = 12345
            context.user_data["questions"] = mock_questions
            context.user_data["index"] = 0
            context.user_data["practice_mode"] = True
            context.user_data["use_timer"] = False
            context.user_data["course_name"] = "Geography"
            context.user_data["chapter_completion"] = True
            
            # Call start_exam_with_polls
            print("  🎯 Starting exam with polls...")
            await start_exam_with_polls(update, context, context.user_data)
            
            # Check if poll was created
            if context.bot.send_poll.called:
                print("  ✅ Poll creation successful")
                poll_call_args = context.bot.send_poll.call_args
                print(f"    - Chat ID: {poll_call_args.kwargs.get('chat_id')}")
                print(f"    - Question: {poll_call_args.kwargs.get('question', '')[:50]}...")
                print(f"    - Options: {poll_call_args.kwargs.get('options')}")
                
                # Store the poll ID that would be created
                mock_poll_id = "mock_poll_12345"
                poll_obj = Mock()
                poll_obj.id = mock_poll_id
                
                # Mock the poll response
                context.bot.send_poll.return_value = Mock()
                context.bot.send_poll.return_value.poll = poll_obj
                
                # Update user data with poll ID
                context.user_data["current_poll_id"] = mock_poll_id
                
                # Simulate poll answer
                print("  📤 Simulating user answering poll...")
                
                poll_answer_update = Mock()
                poll_answer_update.poll_answer = Mock()
                poll_answer_update.poll_answer.poll_id = mock_poll_id
                poll_answer_update.poll_answer.option_ids = [0]  # Select first option
                poll_answer_update.effective_user = Mock()
                poll_answer_update.effective_user.id = 12345
                poll_answer_update.effective_chat = Mock()
                poll_answer_update.effective_chat.id = 12345
                
                # Call handle_poll_answer
                await handle_poll_answer(poll_answer_update, context)
                
                print(f"  📊 After poll answer:")
                print(f"    - Question index: {context.user_data['index']}")
                print(f"    - Total questions: {len(context.user_data['questions'])}")
                print(f"    - Should show next question: {context.user_data['index'] < len(context.user_data['questions'])}")
                
                # Check if next question function was called
                if context.bot.send_poll.call_count > 1:
                    print("  ✅ Next question poll was created")
                    next_poll_call = context.bot.send_poll.call_args
                    print(f"    - Next question: {next_poll_call.kwargs.get('question', '')[:50]}...")
                    return True
                else:
                    print("  ❌ Next question poll was NOT created")
                    print(f"    - send_poll called {context.bot.send_poll.call_count} times total")
                    return False
            else:
                print("  ❌ Initial poll creation failed")
                return False
                
    except Exception as e:
        print(f"  ❌ Practice flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_question_data_validation():
    """Test if question data is properly formatted"""
    print("\n🔍 Testing Question Data Validation...")
    
    try:
        from app.handlers.radio_question_handler import create_poll_question
        
        # Create test question
        question = Mock()
        question.id = 1
        question.text = "What is the capital of France?"
        question.option_a = "London"
        question.option_b = "Berlin"
        question.option_c = "Paris"
        question.option_d = "Madrid"
        question.correct_answer = "C"
        
        # Create poll data
        poll_data = create_poll_question(question, 1, 5)
        
        print(f"  📝 Question text: {poll_data['question']}")
        print(f"  🔘 Options: {poll_data['options']}")
        print(f"  ✅ Correct option ID: {poll_data['correct_option_id']}")
        
        # Validate the data
        if poll_data['correct_option_id'] == 2:  # Paris should be index 2
            print("  ✅ Correct answer mapping is correct")
            return True
        else:
            print("  ❌ Correct answer mapping is wrong")
            return False
            
    except Exception as e:
        print(f"  ❌ Question validation failed: {e}")
        return False

async def test_handler_registration():
    """Test if handlers are properly registered in dispatcher"""
    print("\n📋 Testing Handler Registration...")
    
    try:
        # Check dispatcher registration
        from app.bot.dispatcher_fixed import register_handlers
        
        # Create mock application
        mock_app = Mock()
        mock_app.add_handler = Mock()
        
        # Register handlers
        register_handlers(mock_app)
        
        # Check if PollAnswerHandler was registered
        handlers_called = mock_app.add_handler.call_args_list
        
        poll_handler_registered = False
        for call in handlers_called:
            handler_type = call[0][0]
            if hasattr(handler_type, '__class__'):
                if 'PollAnswerHandler' in str(handler_type.__class__):
                    poll_handler_registered = True
                    break
        
        if poll_handler_registered:
            print("  ✅ PollAnswerHandler is registered")
            return True
        else:
            print("  ❌ PollAnswerHandler is NOT registered")
            print(f"    - Registered handlers: {[str(call[0][0]) for call in handlers_called]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Handler registration test failed: {e}")
        return False

async def main():
    """Run comprehensive diagnostic tests"""
    print("🔍 COMPREHENSIVE BOT DIAGNOSTIC TEST")
    print("=" * 80)
    
    tests = [
        ("Bot Startup", test_bot_startup()),
        ("Question Data Validation", test_question_data_validation()),
        ("Handler Registration", test_handler_registration()),
        ("Complete Practice Flow", test_practice_flow_simulation())
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
    print("\n" + "=" * 80)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed - The issue might be in production environment")
        print("Possible causes:")
        print("  • Bot permissions (needs to send polls)")
        print("  • Telegram API rate limiting")
        print("  • Network connectivity issues")
        print("  • Real question data format issues")
    else:
        print(f"\n❌ {total - passed} test(s) failed - Issues found:")
        for i, (test_name, result) in enumerate(zip([t[0] for t in tests], results)):
            if not result:
                print(f"  • {test_name} failed")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

