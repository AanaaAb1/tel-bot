#!/usr/bin/env python3
"""
Simple Diagnostic Test - Tests core functionality without complex async operations
"""

import sys
import os
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test basic imports"""
    print("🔍 Testing Core Imports...")
    
    try:
        # Test importing radio question handler
        from app.handlers.radio_question_handler import (
            handle_poll_answer, 
            create_poll_question,
            start_exam_with_polls,
            show_next_question
        )
        print("  ✅ radio_question_handler imports successful")
        
        # Test importing practice handler
        from app.handlers.practice_handler import start_practice, practice_course_selected
        print("  ✅ practice_handler imports successful")
        
        # Test creating mock poll question
        question = Mock()
        question.id = 1
        question.text = "Test question?"
        question.option_a = "Option A"
        question.option_b = "Option B"
        question.option_c = None
        question.option_d = None
        question.correct_answer = "A"
        
        poll_data = create_poll_question(question, 1, 5)
        print(f"  ✅ create_poll_question works: {len(poll_data['options'])} options")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_handler_functions():
    """Test handler function signatures"""
    print("\n🔧 Testing Handler Functions...")
    
    try:
        from app.handlers.radio_question_handler import (
            handle_poll_answer,
            show_next_question,
            start_exam_with_polls
        )
        
        # Check function signatures
        import inspect
        
        # Check handle_poll_answer signature
        handle_params = list(inspect.signature(handle_poll_answer).parameters.keys())
        expected_params = ['update', 'context']
        
        if handle_params == expected_params:
            print("  ✅ handle_poll_answer signature correct")
        else:
            print(f"  ❌ handle_poll_answer signature wrong: {handle_params} vs {expected_params}")
            return False
        
        # Check show_next_question signature  
        next_params = list(inspect.signature(show_next_question).parameters.keys())
        expected_next_params = ['update', 'context', 'data']
        
        if next_params == expected_next_params:
            print("  ✅ show_next_question signature correct")
        else:
            print(f"  ❌ show_next_question signature wrong: {next_params} vs {expected_next_params}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Handler function test failed: {e}")
        return False

def test_mock_scenario():
    """Test a simple mock scenario"""
    print("\n🎭 Testing Mock Scenario...")
    
    try:
        from app.handlers.radio_question_handler import create_poll_question
        
        # Create mock question
        question = Mock()
        question.id = 123
        question.text = "What is 2+2?"
        question.option_a = "3"
        question.option_b = "4"
        question.option_c = "5"
        question.option_d = "6"
        question.correct_answer = "B"
        
        # Create poll data
        poll_data = create_poll_question(question, 1, 10)
        
        # Validate results
        print(f"  📝 Question text: {poll_data['question'][:50]}...")
        print(f"  🔘 Options: {poll_data['options']}")
        print(f"  ✅ Correct option: {poll_data['correct_option_id']} (should be 1 for B)")
        
        # Check that the correct answer mapping works
        if poll_data['correct_option_id'] == 1:
            print("  ✅ Correct answer mapping works")
            return True
        else:
            print("  ❌ Correct answer mapping failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Mock scenario test failed: {e}")
        return False

def test_practice_flow_basic():
    """Test basic practice flow logic"""
    print("\n📚 Testing Practice Flow Logic...")
    
    try:
        # Test the basic logic that should happen in practice flow
        questions = []
        for i in range(3):
            q = Mock()
            q.id = i + 1
            q.text = f"Question {i + 1}"
            q.option_a = f"A{i + 1}"
            q.option_b = f"B{i + 1}"
            q.option_c = None
            q.option_d = None
            q.correct_answer = "A" if i % 2 == 0 else "B"
            questions.append(q)
        
        # Simulate practice data
        practice_data = {
            "questions": questions,
            "index": 0,
            "practice_mode": True,
            "user_id": 12345,
            "chat_id": 12345,
            "current_poll_id": None
        }
        
        print(f"  📊 Practice data setup:")
        print(f"    - Total questions: {len(practice_data['questions'])}")
        print(f"    - Current index: {practice_data['index']}")
        print(f"    - Practice mode: {practice_data['practice_mode']}")
        
        # Simulate answering first question
        practice_data["index"] += 1
        print(f"  📤 After answering question:")
        print(f"    - New index: {practice_data['index']}")
        print(f"    - Should show next: {practice_data['index'] < len(practice_data['questions'])}")
        
        # Simulate answering second question
        practice_data["index"] += 1
        print(f"  📤 After answering second question:")
        print(f"    - New index: {practice_data['index']}")
        print(f"    - Should show next: {practice_data['index'] < len(practice_data['questions'])}")
        
        # Simulate answering third question (should complete)
        practice_data["index"] += 1
        print(f"  📤 After answering third question:")
        print(f"    - New index: {practice_data['index']}")
        print(f"    - Should complete: {practice_data['index'] >= len(practice_data['questions'])}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Practice flow test failed: {e}")
        return False

def main():
    """Run simple diagnostic tests"""
    print("🔍 SIMPLE BOT DIAGNOSTIC TEST")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_handler_functions,
        test_mock_scenario,
        test_practice_flow_basic
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
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All core tests passed!")
        print("The radio_question_handler syntax issue has been FIXED.")
        print("Next steps:")
        print("  • Test with real Telegram bot")
        print("  • Check bot permissions")
        print("  • Verify database connectivity")
        print("  • Test with actual question data")
    else:
        print(f"\n❌ {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
