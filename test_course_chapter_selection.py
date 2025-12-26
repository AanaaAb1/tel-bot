#!/usr/bin/env python3
"""
Test script to verify course and chapter selection functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.chapter import Chapter
from app.services.course_service import get_course_by_id
from app.services.chapter_service import get_chapters_by_course
from app.services.question_service import get_questions_by_chapter

def test_course_chapter_selection():
    """Test course and chapter selection functionality"""
    print("=== TESTING COURSE AND CHAPTER SELECTION ===")

    db = SessionLocal()

    try:
        # Test 1: Get all courses
        courses = db.query(Course).all()
        print(f"1. Found {len(courses)} courses:")
        for course in courses:
            print(f"   ID: {course.id}, Name: '{course.name}'")

        # Test 2: Get chapters for each course
        print("\n2. Checking chapters for each course:")
        for course in courses:
            chapters = db.query(Chapter).filter_by(course_id=course.id).all()
            print(f"   Course: {course.name} (ID: {course.id})")
            if chapters:
                print(f"     Found {len(chapters)} chapters:")
                for chapter in chapters:
                    print(f"       Chapter ID: {chapter.id}, Name: '{chapter.name}'")
            else:
                print(f"     No chapters found for {course.name}")

        # Test 3: Test get_course_by_id function
        print("\n3. Testing get_course_by_id function:")
        if courses:
            test_course = get_course_by_id(courses[0].id)
            if test_course:
                print(f"   ✅ get_course_by_id works: {test_course.name}")
            else:
                print("   ❌ get_course_by_id failed")

        # Test 4: Test get_chapters_by_course function
        print("\n4. Testing get_chapters_by_course function:")
        if courses:
            chapters = get_chapters_by_course(courses[0].id)
            if chapters:
                print(f"   ✅ get_chapters_by_course works: found {len(chapters)} chapters")
                for chapter in chapters:
                    print(f"     Chapter: {chapter.name} (ID: {chapter.id})")
            else:
                print("   ❌ get_chapters_by_course returned no chapters")

        # Test 5: Test get_questions_by_chapter function
        print("\n5. Testing get_questions_by_chapter function:")
        all_chapters = db.query(Chapter).all()
        if all_chapters:
            questions = get_questions_by_chapter(all_chapters[0].id)
            print(f"   Chapter: {all_chapters[0].name}")
            if questions:
                print(f"   ✅ get_questions_by_chapter works: found {len(questions)} questions")
            else:
                print("   ❌ get_questions_by_chapter returned no questions (expected if no questions exist)")
        else:
            print("   ❌ No chapters found to test with")

        # Test 6: Simulate the callback data flow
        print("\n6. Testing callback data flow:")
        if courses and chapters:
            course = courses[0]
            chapter = chapters[0]
            
            # Simulate the callback data that would be created
            course_callback = f"exam_course_{course.id}"
            chapter_callback = f"start_exam_{chapter.id}"
            
            print(f"   Course callback: {course_callback}")
            print(f"   Chapter callback: {chapter_callback}")
            
            # Extract IDs from callback data
            extracted_course_id = int(course_callback.replace("exam_course_", ""))
            extracted_chapter_id = int(chapter_callback.replace("start_exam_", ""))
            
            print(f"   Extracted course ID: {extracted_course_id}")
            print(f"   Extracted chapter ID: {extracted_chapter_id}")
            
            if extracted_course_id == course.id and extracted_chapter_id == chapter.id:
                print("   ✅ Callback data flow works correctly")
            else:
                print("   ❌ Callback data flow failed")

        print("\n=== TEST COMPLETED ===")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_course_chapter_selection()
