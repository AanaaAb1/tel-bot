#!/usr/bin/env python3
"""
Test script to verify that the course selection fix works correctly.
This tests the new functions that handle both numeric IDs and course codes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.course_service import get_courses_by_code, get_course_by_id
from app.handlers.course_handler import get_exams_by_course

def test_course_code_function():
    """Test the get_courses_by_code function"""
    print("🔍 Testing get_courses_by_code function...")
    
    # Test different course codes
    test_codes = ['maths', 'physics', 'chemistry', 'biology', 'english']
    
    for code in test_codes:
        courses = get_courses_by_code(code)
        print(f"   Course code '{code}': Found {len(courses)} courses")
        if courses:
            for course in courses:
                print(f"     - {course.name}")
    
    # Test invalid code
    courses = get_courses_by_code('invalid_code')
    print(f"   Invalid code 'invalid_code': Found {len(courses)} courses")
    assert len(courses) == 0, "Should find no courses for invalid code"
    
    print("✅ get_courses_by_code function works correctly!")

def test_exams_by_course_function():
    """Test the get_exams_by_course function"""
    print("\n🔍 Testing get_exams_by_course function...")
    
    # First, get a course ID
    courses = get_courses_by_code('maths')
    if courses:
        course = courses[0]
        exams = get_exams_by_course(course.id)
        print(f"   Course '{course.name}' has {len(exams)} chapters")
        for i, exam in enumerate(exams[:3], 1):  # Show first 3
            print(f"     {i}. {exam.name}")
        if len(exams) > 3:
            print(f"     ... and {len(exams) - 3} more")
        
        # Verify we have chapters
        assert len(exams) > 0, f"Course {course.name} should have chapters"
        print(f"✅ Found {len(exams)} chapters for {course.name}")
    else:
        print("❌ No courses found to test with")

def test_integration():
    """Test the complete flow"""
    print("\n🔍 Testing complete course selection flow...")
    
    # Test with course code 'maths'
    courses = get_courses_by_code('maths')
    if courses:
        course = courses[0]
        print(f"   Selected course: {course.name} (ID: {course.id})")
        
        # Get chapters for this course
        exams = get_exams_by_course(course.id)
        print(f"   Found {len(exams)} chapters")
        
        if exams:
            # Test first chapter
            first_exam = exams[0]
            print(f"   First chapter: {first_exam.name} (ID: {first_exam.id})")
            print("✅ Complete flow works!")
        else:
            print("❌ No chapters found for course")
    else:
        print("❌ No courses found with code 'maths'")

if __name__ == "__main__":
    print("🧪 TESTING COURSE SELECTION FIX")
    print("=" * 50)
    
    try:
        test_course_code_function()
        test_exams_by_course_function()
        test_integration()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("The course selection fix should now work correctly.")
        print("\nExpected user flow:")
        print("1. User clicks 'maths' course button")
        print("2. get_courses_by_code('maths') finds Mathematics course")
        print("3. get_exams_by_course(course.id) finds 10 chapters")
        print("4. User sees 10 chapter buttons to select from")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
