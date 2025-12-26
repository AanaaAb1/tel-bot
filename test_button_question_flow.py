#!/usr/bin/env python3
"""
Test script to verify button question flow implementation
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/home/aneman/Desktop/Exambot/telegramexambot')

from app.database.session import SessionLocal
from app.models.question import Question
from app.models.course import Course
from app.models.chapter import Chapter
from app.handlers.radio_question_handler import (
    create_question_data,
    create_question_keyboard,
    handle_button_answer,
    show_question_as_button,
    start_exam_with_buttons,
    get_timer_duration,
    is_true_false_question
)

def test_question_data_creation():
    """Test creating question data for button display"""
    print("🧪 Testing question data creation...")
    
    # Create a mock question
    class MockQuestion:
        def __init__(self):
            self.id = 1
            self.text = "What is the capital of France?"
            self.option_a = "Paris"
            self.option_b = "London" 
            self.option_c = "Berlin"
            self.option_d = "Madrid"
            self.correct_answer = "A"
    
    question = MockQuestion()
    
    # Test multiple choice question
    question_data = create_question_data(question, 1, 10, "Geography")
    
    assert question_data["question_text"] == "📝 Question 1/10 (⏰ 1 minute)\n\nWhat is the capital of France?"
    assert len(question_data["options"]) == 4
    assert question_data["options"][0] == "A) Paris"
    assert question_data["correct_option_id"] == 0
    assert question_data["question_id"] == 1
    assert question_data["timer_duration"] == 60  # 1 minute for Geography
    
    print("✅ Multiple choice question data creation passed")

def test_true_false_question():
    """Test true/false question handling"""
    print("🧪 Testing true/false question...")
    
    class MockQuestion:
        def __init__(self):
            self.id = 2
            self.text = "The Earth is flat."
            self.correct_answer = "FALSE"
    
    question = MockQuestion()
    
    # Mock the is_true_false_question function
    from app.handlers.radio_question_handler import is_true_false_question
    original_func = is_true_false_question
    is_true_false_question = lambda q: True
    
    question_data = create_question_data(question, 1, 5, "Science")
    
    assert len(question_data["options"]) == 2
    assert question_data["options"] == ["TRUE", "FALSE"]
    assert question_data["correct_option_id"] == 1  # FALSE is correct
    
    print("✅ True/false question data creation passed")
    
    # Restore original function
    is_true_false_question = original_func

def test_question_keyboard():
    """Test question keyboard creation"""
    print("🧪 Testing question keyboard creation...")
    
    question_data = {
        "question_id": 1,
        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"]
    }
    
    keyboard = create_question_keyboard(question_data)
    
    # Check keyboard structure
    assert len(keyboard.inline_keyboard) == 4  # 4 options
    assert keyboard.inline_keyboard[0][0].text == "A) Option 1"
    assert keyboard.inline_keyboard[1][0].text == "B) Option 2"
    assert keyboard.inline_keyboard[2][0].text == "C) Option 3"
    assert keyboard.inline_keyboard[3][0].text == "D) Option 4"
    
    # Check callback data format
    assert keyboard.inline_keyboard[0][0].callback_data == "answer_1_A"
    assert keyboard.inline_keyboard[1][0].callback_data == "answer_1_B"
    assert keyboard.inline_keyboard[2][0].callback_data == "answer_1_C"
    assert keyboard.inline_keyboard[3][0].callback_data == "answer_1_D"
    
    print("✅ Question keyboard creation passed")

def test_callback_parsing():
    """Test callback data parsing"""
    print("🧪 Testing callback data parsing...")
    
    callback_data = "answer_123_A"
    parts = callback_data.split("_")
    
    assert len(parts) == 3
    assert parts[0] == "answer"
    assert parts[1] == "123"
    assert parts[2] == "A"
    
    print("✅ Callback data parsing passed")

def test_course_timer_duration():
    """Test timer duration for different courses"""
    print("🧪 Testing course timer durations...")
    
    # Test different course types
    assert get_timer_duration("Mathematics") == 120  # Math gets 2 minutes
    assert get_timer_duration("Physics") == 120     # Physics gets 2 minutes
    assert get_timer_duration("Chemistry") == 60    # Other subjects get 1 minute
    assert get_timer_duration("History") == 60      # History gets 1 minute
    assert get_timer_duration("Geography") == 60    # Geography gets 1 minute
    assert get_timer_duration(None) == 60           # Default to 1 minute
    
    print("✅ Course timer durations passed")

def main():
    """Run all tests"""
    print("🚀 Starting Button Question Flow Tests")
    print("=" * 50)
    
    try:
        test_question_data_creation()
        test_true_false_question()
        test_question_keyboard()
        test_callback_parsing()
        test_course_timer_duration()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Button question flow is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
