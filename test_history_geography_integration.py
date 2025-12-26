#!/usr/bin/env python3
"""
Simple test to verify History appears in exam system alongside Geography
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.exam import Exam
from app.keyboards.course_keyboard import course_keyboard

def test_history_and_geography_in_exam_system():
    """Test that both History and Geography are properly integrated"""
    print("🧪 TESTING HISTORY & GEOGRAPHY IN EXAM SYSTEM")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Test 1: Both courses exist
        print("1️⃣ Checking History & Geography courses...")
        geography_course = db.query(Course).filter(Course.name == "Geography").first()
        history_course = db.query(Course).filter(Course.name == "History").first()
        
        if not geography_course:
            print("❌ Geography course not found!")
            return False
        
        if not history_course:
            print("❌ History course not found!")
            return False
        
        print(f"✅ Geography course found (ID: {geography_course.id})")
        print(f"✅ History course found (ID: {history_course.id})")
        
        # Test 2: Both have chapters
        print("\n2️⃣ Checking History & Geography chapters...")
        geography_chapters = db.query(Exam).filter(Exam.course_id == geography_course.id).all()
        history_chapters = db.query(Exam).filter(Exam.course_id == history_course.id).all()
        
        if len(geography_chapters) < 10:
            print(f"❌ Only {len(geography_chapters)} Geography chapters found!")
            return False
        
        if len(history_chapters) < 10:
            print(f"❌ Only {len(history_chapters)} History chapters found!")
            return False
        
        print(f"✅ Geography has {len(geography_chapters)} chapters")
        print(f"✅ History has {len(history_chapters)} chapters")
        
        # Test 3: Both appear in course keyboard
        print("\n3️⃣ Checking course keyboard...")
        keyboard = course_keyboard()
        
        geography_found = False
        history_found = False
        
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Geography" in button.text:
                    geography_found = True
                    print(f"✅ Geography button: '{button.text}' -> {button.callback_data}")
                elif "History" in button.text:
                    history_found = True
                    print(f"✅ History button: '{button.text}' -> {button.callback_data}")
        
        if not geography_found:
            print("❌ Geography not found in course keyboard!")
            return False
        
        if not history_found:
            print("❌ History not found in course keyboard!")
            return False
        
        # Test 4: List all courses available
        print("\n4️⃣ All available courses:")
        all_courses = db.query(Course).all()
        for course in all_courses:
            chapter_count = db.query(Exam).filter(Exam.course_id == course.id).count()
            print(f"   📚 {course.name:<15} | Chapters: {chapter_count:2d}/10 | {'✅' if chapter_count >= 10 else '❌'}")
        
        # Test 5: List History chapters
        print(f"\n5️⃣ History chapters available:")
        for i, chapter in enumerate(history_chapters, 1):
            print(f"   {i:2d}. {chapter.name}")
        
        print(f"\n🎉 SUCCESS! Both History & Geography are working!")
        print(f"📚 Total courses in system: {len(all_courses)}")
        print(f"🌍 Geography chapters: {len(geography_chapters)}")
        print(f"📜 History chapters: {len(history_chapters)}")
        print(f"✅ Users can now select History from exam menu")
        print(f"✅ Users can now select Geography from exam menu")
        print(f"✅ Both courses are ready for exams!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_history_and_geography_in_exam_system()
    if success:
        print("\n🌍📜 BOTH GEOGRAPHY & HISTORY ARE READY FOR EXAMS!")
    else:
        print("\n❌ System has issues!")
