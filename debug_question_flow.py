#!/usr/bin/env python3
"""
Debug script to identify why next question is not showing after user answers.
"""

import sys
import os
sys.path.append('/home/aneman/Desktop/Exambot/telegramexambot')

from unittest.mock import Mock, MagicMock, patch
from app.handlers.radio_question_handler import handle_poll_answer, show_next_question, show_question_as_poll
from app.database.session import SessionLocal
from app.models.answer import Answer

def debug_question_flow():
    """Debug the question flow to identify issues"""
    
    print("🔍 Debugging Question Flow Issue...")
    print("=" * 50)
    
    # Mock update object
    update = Mock()
    update.effective_user.id = 12345
    update.effective_message = Mock()
    update.poll_answer = Mock()
    
    # Mock poll answer with first option selected
    update.poll_answer.poll_id = "poll_123"
    update.poll_answer.option_ids = [0]  # Select first option (A)
    
    # Mock context with user data
    context = Mock()
    context.user_data = {
        "current_poll_id": "poll_123",
        "user_id": 12345,
        "questions": [
            Mock(id=1, correct_answer="A", text="What is 2+2?", option_a="4", option_b="3", option_c="5", option_d="6"),
            Mock(id=2, correct_answer="B", text="What is 3+3?", option_a="5", option_b="6", option_c="7", option_d="8"),
            Mock(id=3, correct_answer="C", text="What is 4+4?", option_a="7", option_b="8", option_c="9", option_d="10"),
        ],
        "index": 0,
        "practice_mode": True,
        "chapter_completion": True,
        "chat_id": 98765
    }
    
    print("✅ Mock setup complete")
    
    # Test 1: Check if current_poll_id matches
    current_poll_id = context.user_data.get("current_poll_id")
    incoming_poll_id = update.poll_answer.poll_id
    
    if current_poll_id == incoming_poll_id:
        print("✅ Poll ID matches - should process answer")
    else:
        print(f"❌ Poll ID mismatch - Current: {current_poll_id}, Incoming: {incoming_poll_id}")
    
    # Test 2: Check question index and progression
    current_index = context.user_data.get("index", 0)
    total_questions = len(context.user_data.get("questions", []))
    
    print(f"📊 Current question index: {current_index}")
    print(f"📊 Total questions: {total_questions}")
    print(f"📊 Should show next question: {current_index < total_questions}")
    
    # Test 3: Check selected option processing
    selected_option_ids = update.poll_answer.option_ids
    if selected_option_ids:
        selected_option_id = selected_option_ids[0]
        option_letters = ['A', 'B', 'C', 'D']
        selected_option = option_letters[selected_option_id] if selected_option_id < len(option_letters) else 'A'
        print(f"✅ Selected option: {selected_option}")
        
        # Check if it's correct
        current_question = context.user_data["questions"][current_index]
        is_correct = selected_option == current_question.correct_answer
        print(f"✅ Answer correctness: {is_correct}")
    
    # Test 4: Simulate the flow logic
    print("\n🔄 Simulating question flow logic:")
    
    # Step 1: User answers question
    print(f"1️⃣ User answered question {current_index + 1}")
    
    # Step 2: Increment index
    context.user_data["index"] += 1
    new_index = context.user_data["index"]
    print(f"2️⃣ Index incremented to: {new_index}")
    
    # Step 3: Check if more questions remain
    if new_index < total_questions:
        print(f"3️⃣ More questions available - should show question {new_index + 1}")
        next_question = context.user_data["questions"][new_index]
        print(f"   Next question: {next_question.text}")
    else:
        print("3️⃣ No more questions - should show chapter completion")
    
    # Step 4: Clear current poll ID
    context.user_data["current_poll_id"] = None
    print("4️⃣ Current poll ID cleared")
    
    return True

def test_question_progression():
    """Test the question progression logic"""
    
    print("\n🧪 Testing Question Progression Logic...")
    print("=" * 50)
    
    # Test scenario 1: Normal progression (3 questions)
    user_data = {
        "questions": [Mock(), Mock(), Mock()],
        "index": 0,
        "current_poll_id": "poll_123"
    }
    
    for i in range(4):  # Test 4 steps (including after last question)
        current_index = user_data["index"]
        total_questions = len(user_data["questions"])
        
        print(f"\nStep {i + 1}:")
        print(f"  Current index: {current_index}")
        print(f"  Total questions: {total_questions}")
        
        if current_index < total_questions:
            print(f"  ✅ Should show question {current_index + 1}")
            
            # Simulate answering
            user_data["index"] += 1
            user_data["current_poll_id"] = None
            
            print(f"  ✅ Answered, moved to index {user_data['index']}")
        else:
            print(f"  ❌ No more questions - should show completion")
            break
    
    return True

def test_poll_answer_handling():
    """Test the poll answer handling logic"""
    
    print("\n🧪 Testing Poll Answer Handling...")
    print("=" * 50)
    
    # Mock data similar to real scenario
    user_data = {
        "current_poll_id": "poll_123",
        "questions": [
            Mock(id=1, correct_answer="A"),
            Mock(id=2, correct_answer="B"), 
            Mock(id=3, correct_answer="C")
        ],
        "index": 0,
        "practice_mode": True,
        "chapter_completion": True,
        "user_id": 12345
    }
    
    # Simulate user answering question 1
    print("🔄 Simulating user answering question 1...")
    
    # Check if should process answer
    if "current_poll_id" in user_data and user_data["current_poll_id"] == "poll_123":
        print("✅ Should process poll answer")
        
        # Check selected option
        selected_option_id = 0  # Option A
        option_letters = ['A', 'B', 'C', 'D']
        selected_option = option_letters[selected_option_id]
        print(f"✅ Selected option: {selected_option}")
        
        # Check correctness
        question = user_data["questions"][user_data["index"]]
        is_correct = selected_option == question.correct_answer
        print(f"✅ Is correct: {is_correct}")
        
        # Move to next question
        user_data["index"] += 1
        user_data["current_poll_id"] = None
        
        print(f"✅ Moved to next question (index: {user_data['index']})")
        
        # Check if should show next question or completion
        if user_data["index"] < len(user_data["questions"]):
            print("✅ Should show next question")
        else:
            print("✅ Should show chapter completion")
    else:
        print("❌ Should not process poll answer")
    
    return True

def main():
    """Run all debug tests"""
    print("🚀 Starting Question Flow Debug")
    print("=" * 60)
    
    try:
        debug_question_flow()
        test_question_progression()
        test_poll_answer_handling()
        
        print("\n" + "=" * 60)
        print("🎉 DEBUG ANALYSIS COMPLETE!")
        print("\n📋 Potential Issues to Check:")
        print("• Database connection when saving answers")
        print("• Question retrieval for next question")
        print("• Message sending for next question")
        print("• Poll timer cancellation")
        print("• User data state management")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
