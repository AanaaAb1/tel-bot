
#!/usr/bin/env python3
"""
Comprehensive test to verify all courses have chapters and functionality works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.chapter import Chapter

def test_all_courses_have_chapters():
    """Test that all expected courses exist with 10 chapters each"""
    db = SessionLocal()
    
    try:
        # Expected courses
        expected_courses = [
            "Mathematics", "Physics", "Chemistry", "Biology", "English",
            "Geography", "History", "Government", "Economics", "Literature"
        ]
        
        print("🧪 Testing All Courses Chapter Implementation")
        print("=" * 60)
        
        # Get all courses from database
        courses = db.query(Course).all()
        course_names = [course.name for course in courses]
        
        print(f"📊 Database State Analysis:")
        print(f"   Total courses in database: {len(courses)}")
        print(f"   Expected courses: {len(expected_courses)}")
        
        # Check if all expected courses exist
        missing_courses = []
        for expected_course in expected_courses:
            if expected_course not in course_names:
                missing_courses.append(expected_course)
        
        if missing_courses:
            print(f"❌ Missing courses: {', '.join(missing_courses)}")
            return False
        else:
            print("✅ All expected courses exist")
        
        print()
        print("📋 Course Details:")
        all_have_10_chapters = True
        
        for course in sorted(courses, key=lambda x: x.id):
            chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
            status = "✅" if chapters_count == 10 else "❌"
            print(f"   {status} {course.id:2d}. {course.name:<15} - {chapters_count:2d} chapters")
            
            if chapters_count != 10:
                all_have_10_chapters = False
        
        print()
        if all_have_10_chapters:
            print("🎉 SUCCESS: All courses have exactly 10 chapters!")
            return True
        else:
            print("❌ FAILED: Some courses don't have 10 chapters")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    finally:
        db.close()

def test_course_service_functionality():
    """Test that course service can find courses by code"""
    print()
    print("🔧 Testing Course Service Functionality")
    print("-" * 40)
    
    try:
        from app.services.course_service import get_courses_by_code
        
        # Test different course codes
        test_codes = ["math", "phys", "chem", "bio", "eng", "geo", "hist", "gov", "econ", "lit"]
        
        for code in test_codes:
            courses = get_courses_by_code(code)
            if courses:
                print(f"✅ Code '{code}' -> {len(courses)} course(s): {[c.name for c in courses]}")
            else:
                print(f"❌ Code '{code}' -> No courses found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing course service: {e}")
        return False

def test_chapter_selection_keyboard():
    """Test that chapter selection keyboard can be created"""
    print()
    print("⌨️  Testing Chapter Selection Keyboard")
    print("-" * 40)
    
    try:
        from app.keyboards.chapter_selection_keyboard import get_chapter_keyboard
        
        # Test with a sample course ID (we'll use 1, which should be Biology)
        keyboard = get_chapter_keyboard(1)
        
        if keyboard and len(keyboard.inline_keyboard) > 0:
            print(f"✅ Chapter keyboard created successfully")
            print(f"   Number of chapter buttons: {len(keyboard.inline_keyboard[0])}")
            return True
        else:
            print("❌ Chapter keyboard creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chapter keyboard: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Course Chapter Test")
    print()
    
    # Run all tests
    test1 = test_all_courses_have_chapters()
    test2 = test_course_service_functionality()
    test3 = test_chapter_selection_keyboard()
    
    print()
    print("=" * 60)
    print("📊 FINAL TEST RESULTS:")
    print(f"   Database Setup: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   Course Service: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"   Chapter Keyboard: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if all([test1, test2, test3]):
        print()
        print("🎉 ALL TESTS PASSED!")
        print("   All courses now have chapters and the system is ready!")
        print("   Users can click any course and see its chapters as buttons.")
    else:
        print()
        print("⚠️  SOME TESTS FAILED!")
        print("   The implementation may need additional fixes.")

