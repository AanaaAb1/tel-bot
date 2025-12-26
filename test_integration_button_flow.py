#!/usr/bin/env python3
"""
Integration test for button question flow transformation
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/home/aneman/Desktop/Exambot/telegramexambot')

def test_dispatcher_import():
    """Test that dispatcher imports work correctly"""
    print("🧪 Testing dispatcher imports...")
    
    try:
        from app.bot.dispatcher_fixed import register_handlers
        print("✅ Dispatcher import successful")
        return True
    except Exception as e:
        print(f"❌ Dispatcher import failed: {e}")
        return False

def test_radio_handler_integration():
    """Test radio handler integration with dispatcher"""
    print("🧪 Testing radio handler integration...")
    
    try:
        # Test imports
        from app.handlers.radio_question_handler import handle_button_answer
        from app.handlers.radio_question_handler import create_question_data
        from app.handlers.radio_question_handler import create_question_keyboard
        
        print("✅ Radio handler imports successful")
        
        # Test function signatures
        assert callable(handle_button_answer)
        assert callable(create_question_data)
        assert callable(create_question_keyboard)
        
        print("✅ Radio handler functions are callable")
        return True
    except Exception as e:
        print(f"❌ Radio handler integration failed: {e}")
        return False

def test_database_models():
    """Test database models integration"""
    print("🧪 Testing database models...")
    
    try:
        from app.models.question import Question
        from app.models.course import Course
        from app.models.chapter import Chapter
        
        print("✅ Database models import successful")
        
        # Test model attributes
        assert hasattr(Question, 'text')
        assert hasattr(Question, 'option_a')
        assert hasattr(Question, 'option_b')
        assert hasattr(Question, 'option_c')
        assert hasattr(Question, 'option_d')
        assert hasattr(Question, 'correct_answer')
        
        print("✅ Database models have required attributes")
        return True
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False

def test_question_flow_simulation():
    """Simulate a complete question flow"""
    print("🧪 Testing question flow simulation...")
    
    try:
        from app.handlers.radio_question_handler import (
            create_question_data, 
            create_question_keyboard,
            get_timer_duration
        )
        
        # Create mock question
        class MockQuestion:
            def __init__(self):
                self.id = 1
                self.text = "What is 2+2?"
                self.option_a = "3"
                self.option_b = "4"
                self.option_c = "5"
                self.option_d = "6"
                self.correct_answer = "B"
        
        question = MockQuestion()
        
        # Test question data creation
        question_data = create_question_data(question, 1, 10, "Mathematics")
        assert "question_text" in question_data
        assert "options" in question_data
        assert "correct_option_id" in question_data
        assert question_data["correct_option_id"] == 1  # B = 1
        
        # Test keyboard creation
        keyboard = create_question_keyboard(question_data)
        assert len(keyboard.inline_keyboard) == 4
        
        # Test timer duration
        duration = get_timer_duration("Mathematics")
        assert duration == 120  # Math gets 2 minutes
        
        print("✅ Question flow simulation successful")
        return True
    except Exception as e:
        print(f"❌ Question flow simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_callback_data_format():
    """Test callback data format consistency"""
    print("🧪 Testing callback data format...")
    
    try:
        from app.handlers.radio_question_handler import create_question_keyboard
        
        # Create test question data
        question_data = {
            "question_id": 123,
            "options": ["A) Option A", "B) Option B", "C) Option C", "D) Option D"]
        }
        
        keyboard = create_question_keyboard(question_data)
        
        # Verify callback data format
        for i, row in enumerate(keyboard.inline_keyboard):
            callback_data = row[0].callback_data
            expected_format = f"answer_123_{chr(65 + i)}"  # A, B, C, D
            assert callback_data == expected_format, f"Expected {expected_format}, got {callback_data}"
        
        print("✅ Callback data format is correct")
        return True
    except Exception as e:
        print(f"❌ Callback data format test failed: {e}")
        return False

def test_dispatcher_handler_registration():
    """Test that dispatcher properly registers handlers"""
    print("🧪 Testing dispatcher handler registration...")
    
    try:
        # Mock application object
        class MockApp:
            def __init__(self):
                self.handlers = []
            
            def add_handler(self, handler, group=None):
                self.handlers.append(handler)
        
        mock_app = MockApp()
        
        # Test handler registration
        from app.bot.dispatcher_fixed import register_handlers
        register_handlers(mock_app)
        
        # Check that handlers were added
        assert len(mock_app.handlers) > 0
        
        # Check for CallbackQueryHandler (button answers)
        callback_handlers = [h for h in mock_app.handlers if hasattr(h, 'callback') and 'answer_' in str(h.callback.pattern)]
        assert len(callback_handlers) > 0
        
        print("✅ Dispatcher handler registration successful")
        return True
    except Exception as e:
        print(f"❌ Dispatcher handler registration failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Button Question Flow Integration Tests")
    print("=" * 60)
    
    tests = [
        test_dispatcher_import,
        test_radio_handler_integration,
        test_database_models,
        test_question_flow_simulation,
        test_callback_data_format,
        test_dispatcher_handler_registration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Button question flow is fully functional.")
        return True
    else:
        print("❌ Some integration tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
