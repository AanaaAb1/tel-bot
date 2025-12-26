#!/usr/bin/env python3
"""
Script to update radio_question_handler.py to include timer functionality
"""

import re

def update_radio_handler():
    """Update the radio_question_handler.py file to include timer functionality"""
    
    file_path = "/home/aneman/Desktop/Exambot/telegramexambot/app/handlers/radio_question_handler.py"
    
    # Read the current file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📝 Original create_poll_question function signature:")
    # Find the function signature
    signature_match = re.search(r'def create_poll_question\([^)]+\):', content)
    if signature_match:
        print(f"Found: {signature_match.group()}")
    
    # Update the function signature to include course_name parameter
    old_signature = r'def create_poll_question\(question, question_number, total_questions\):'
    new_signature = 'def create_poll_question(question, question_number, total_questions, course_name=None):'
    
    content = re.sub(old_signature, new_signature, content)
    
    # Update the return statement to include timer information
    old_return = r'return \{\s*"question": f"📝 Question \{question_number\}/\{total_questions\}\\n\\n\{question\.text\}",\s*"options": labeled_options,\s*"correct_option_id": correct_option_id,\s*"question_id": question\.id\s*\}'
    
    new_return = '''    # Get timer duration for this course
    timer_duration = get_timer_duration(course_name)
    timer_text = f"⏰ {timer_duration//60} minute{'s' if timer_duration > 60 else ''}"
    
    return {
        "question": f"📝 Question {question_number}/{total_questions} ({timer_text})\\n\\n{question.text}",
        "options": labeled_options,
        "correct_option_id": correct_option_id,
        "question_id": question.id,
        "timer_duration": timer_duration
    }'''
    
    # Replace the return statement
    content = re.sub(old_return, new_return, content, flags=re.MULTILINE | re.DOTALL)
    
    # Write the updated content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully updated radio_question_handler.py with timer functionality!")
    
    # Test the updated file by importing and testing the function
    try:
        import sys
        sys.path.append('/home/aneman/Desktop/Exambot/telegramexambot')
        
        from app.handlers.radio_question_handler import get_timer_duration, create_poll_question
        
        # Test the timer duration function
        print("\n🧪 Testing updated timer functionality:")
        test_cases = [
            ("Mathematics", 120),
            ("Biology", 60),
            ("", 60),
        ]
        
        for course_name, expected in test_cases:
            actual = get_timer_duration(course_name)
            status = "✅ PASS" if actual == expected else "❌ FAIL"
            print(f"{status} {course_name or 'None':<12} -> {actual}s (expected {expected}s)")
        
        # Test create_poll_question function with a mock question
        class MockQuestion:
            def __init__(self):
                self.id = 1
                self.text = "What is 2+2?"
                self.correct_answer = "A"
                self.option_a = "4"
                self.option_b = "3"
                self.option_c = "5"
                self.option_d = "6"
        
        mock_question = MockQuestion()
        
        # Test with Mathematics course (2 minutes)
        result = create_poll_question(mock_question, 1, 5, "Mathematics")
        print(f"\n📋 Test result for Mathematics course:")
        print(f"Question: {result['question'][:50]}...")
        print(f"Timer Duration: {result['timer_duration']}s")
        print(f"Expected: 120s")
        print(f"Status: {'✅ PASS' if result['timer_duration'] == 120 else '❌ FAIL'}")
        
        # Test with Biology course (1 minute)
        result = create_poll_question(mock_question, 2, 5, "Biology")
        print(f"\n📋 Test result for Biology course:")
        print(f"Question: {result['question'][:50]}...")
        print(f"Timer Duration: {result['timer_duration']}s")
        print(f"Expected: 60s")
        print(f"Status: {'✅ PASS' if result['timer_duration'] == 60 else '❌ FAIL'}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing updated functionality: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_radio_handler()
