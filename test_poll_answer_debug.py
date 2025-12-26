#!/usr/bin/env python3
"""
Test script to debug the poll answer handling issue
This will simulate the exact scenario the user reported
"""

import sys
import asyncio
import logging
from unittest.mock import Mock, AsyncMock
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_poll_answer_flow():
    """Test the exact flow that user reported as failing"""
    
    # Import the handler
    from app.handlers.radio_question_handler import handle_poll_answer, create_poll_question, show_next_question
    
    # Create mock objects to simulate user interaction
    print("🧪 Testing Poll Answer Flow...")
    
    # Create mock poll answer (simulating user answering question 1/6)
    mock_poll_answer = Mock()
    mock_poll_answer.poll_id = "test_poll_12345"
    mock_poll_answer.option_ids = [0]  # User selected option A
    mock_poll_answer.user = Mock()
    mock_poll_answer.user.id = 123456789
    
    # Create mock update object
    mock_update = Mock()
    mock_update.poll_answer = mock_poll_answer
    mock_update.effective_user = Mock()
    mock_update.effective_user.id = 123456789
    mock_update.effective_chat = Mock()
    mock_update.effective_chat.id = 123456789
    
    # Create mock context with user data
    mock_context = Mock()
    mock_context.user_data = {
        "user_id": 123456789,
        "questions": [
            Mock(id=1, text="Question 1?", option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="A"),
            Mock(id=2, text="Question 2?", option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="B"),
            Mock(id=3, text="Question 3?", option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="C"),
            Mock(id=4, text="Question 4?", option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="D"),
            Mock(id=5, text="Question 5?", option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="A"),
            Mock(id=6, text="Question 6?", option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="B"),
        ],
        "index": 0,  # Currently on question 1 (0-indexed)
        "current_poll_id": "test_poll_12345",
        "chat_id": 123456789,
        "practice_mode": True
    }
    
    # Mock the bot to prevent actual API calls
    mock_bot = AsyncMock()
    mock_bot.send_poll = AsyncMock()
    mock_bot.send_poll.return_value = Mock()
    mock_bot.send_poll.return_value.poll = Mock()
    mock_bot.send_poll.return_value.poll.id = "next_poll_67890"
    
    mock_context.bot = mock_bot
    
    # Mock the effective_message for completion handlers
    mock_message = Mock()
    mock_update.effective_message = mock_message
    mock_message.reply_text = AsyncMock()
    
    print(f"📊 Initial state: index={mock_context.user_data['index']}, total_questions={len(mock_context.user_data['questions'])}")
    print(f"🎯 Current question: {mock_context.user_data['questions'][mock_context.user_data['index']].text}")
    print(f"💬 Chat ID: {mock_context.user_data['chat_id']}")
    
    try:
        # Call the poll answer handler
        print("🚀 Calling handle_poll_answer...")
        await handle_poll_answer(mock_update, mock_context)
        print("✅ handle_poll_answer completed successfully")
        
        # Check the updated state
        print(f"📊 Final state: index={mock_context.user_data['index']}, total_questions={len(mock_context.user_data['questions'])}")
        print(f"🔄 Next question should be: {mock_context.user_data['questions'][mock_context.user_data['index']].text}")
        
        # Verify bot.send_poll was called (indicating next question was sent)
        if mock_bot.send_poll.called:
            print("✅ Next question was sent successfully!")
            call_args = mock_bot.send_poll.call_args
            print(f"📤 Poll sent to chat: {call_args.kwargs.get('chat_id')}")
            print(f"📝 Question text: {call_args.kwargs.get('question', '')[:100]}...")
            print(f"🎯 Options: {call_args.kwargs.get('options')}")
        else:
            print("❌ No poll was sent - this indicates the issue!")
            
        # Check if completion handler was called instead
        if mock_message.reply_text.called:
            print("📋 Completion handler was called instead of next question")
            call_args = mock_message.reply_text.call_args
            print(f"💬 Completion message: {call_args.kwargs.get('text', '')[:200]}...")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_show_next_question_directly():
    """Test show_next_question function directly"""
    
    print("\n🔧 Testing show_next_question function directly...")
    
    from app.handlers.radio_question_handler import show_next_question
    
    # Create mock context
    mock_context = Mock()
    mock_context.user_data = {
        "user_id": 123456789,
        "questions": [
            Mock(id=2, text="Question 2?", option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="B"),
            Mock(id=3, text="Question 3?", option_a="A", option_b="B", option_c="C", option_d="D", correct_answer="C"),
        ],
        "index": 0,  # Currently on question 2 (0-indexed for questions list)
        "chat_id": 123456789,
        "current_poll_id": None
    }
    
    # Mock the bot
    mock_bot = AsyncMock()
    mock_bot.send_poll = AsyncMock()
    mock_bot.send_poll.return_value = Mock()
    mock_bot.send_poll.return_value.poll = Mock()
    mock_bot.send_poll.return_value.poll.id = "next_poll_67890"
    
    mock_context.bot = mock_bot
    
    # Create mock update
    mock_update = Mock()
    mock_update.effective_chat = Mock()
    mock_update.effective_chat.id = 123456789
    
    try:
        print("🚀 Calling show_next_question directly...")
        await show_next_question(mock_update, mock_context)
        
        if mock_bot.send_poll.called:
            print("✅ show_next_question works correctly!")
            call_args = mock_bot.send_poll.call_args
            print(f"📤 Poll sent to chat: {call_args.kwargs.get('chat_id')}")
            print(f"📝 Question text: {call_args.kwargs.get('question', '')[:100]}...")
        else:
            print("❌ show_next_question failed to send poll!")
            
    except Exception as e:
        print(f"❌ Exception in show_next_question: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("🔍 POLL ANSWER DEBUG TEST")
    print("=" * 50)
    
    # Test 1: Full poll answer flow
    await test_poll_answer_flow()
    
    # Test 2: Direct show_next_question test
    await test_show_next_question_directly()
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
