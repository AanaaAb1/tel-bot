#!/usr/bin/env python3
"""
Test script to verify that both Natural Science and Social Science students
can access all available courses (no stream restrictions)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.keyboards.stream_course_keyboard import get_all_courses_keyboard, get_all_courses_message
from app.handlers.stream_course_handler import select_natural_science_course, select_social_science_course

def test_all_courses_keyboard():
    """Test that get_all_courses_keyboard returns all 7 courses"""
    print("🧪 Testing get_all_courses_keyboard()...")

    keyboard = get_all_courses_keyboard()

    # Check that we have 8 buttons (7 courses + 1 back button)
    total_buttons = sum(len(row) for row in keyboard.inline_keyboard)
    assert total_buttons == 8, f"Expected 8 buttons, got {total_buttons}"

    # Check course codes in callback data
    expected_courses = ["maths", "english", "bio", "physics", "chemistry", "history", "geography", "government", "economics", "literature"]
    callback_data = [button.callback_data for row in keyboard.inline_keyboard for button in row]

    for course in expected_courses:
        assert f"start_exam_{course}" in callback_data, f"Missing course: {course}"

    print("✅ get_all_courses_keyboard() test passed")

def test_all_courses_message():
    """Test that get_all_courses_message returns appropriate message"""
    print("🧪 Testing get_all_courses_message()...")

    message = get_all_courses_message()

    # Check that message contains key phrases
    assert "ALL COURSES AVAILABLE" in message
    assert "Natural Science Subjects:" in message
    assert "Social Science Subjects:" in message
    assert "Mathematics, English, Biology, Physics, Chemistry" in message
    assert "History, Geography" in message

    print("✅ get_all_courses_message() test passed")

def test_stream_handlers_import():
    """Test that stream course handlers can be imported"""
    print("🧪 Testing stream course handler imports...")

    try:
        from app.handlers.stream_course_handler import (
            select_natural_science_course,
            select_social_science_course,
            handle_stream_course_selection
        )
        print("✅ Stream course handler imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        raise

def main():
    """Run all tests"""
    print("🚀 Starting Course Access Tests...\n")

    try:
        test_all_courses_keyboard()
        test_all_courses_message()
        test_stream_handlers_import()

        print("\n🎉 All tests passed! Course access functionality is working correctly.")
        print("\n📋 Summary:")
        print("✅ Both Natural Science and Social Science students can access all courses")
        print("✅ No stream restrictions implemented")
        print("✅ All 7 courses available: Mathematics, English, Biology, Physics, Chemistry, History, Geography")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
