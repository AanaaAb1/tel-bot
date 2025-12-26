#!/usr/bin/env python3
"""
Simple test to verify Geography appears in exam flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.exam import Exam
from app.keyboards.course_keyboard import course_keyboard

def test_geography_in_exam_system():
    """Test that Geography is properly integrated in the exam system"""
    print("🧪 TESTING GEOGRAPHY IN EXAM SYSTEM")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Test 1: Geography course exists
        print("1️⃣ Checking Geography course...")
        geography_course = db.query(Course).filter(Course.name == "Geography").first()
        
        if not geography_course:
            print("❌ Geography course not found!")
            return False
        
        print(f"✅ Geography course found (ID: {geography_course.id})")
        
        # Test 2: Geography has chapters
        print("\n2️⃣ Checking Geography chapters...")
        chapters = db.query(Exam).filter(Exam.course_id == geography_course.id).all()
        
        if len(chapters) < 10:
            print(f"❌ Only {len(chapters)} chapters found, need 10!")
            return False
        
        print(f"✅ Geography has {len(chapters)} chapters")
        
        # Test 3: Geography appears in course keyboard
        print("\n3️⃣ Checking course keyboard...")
        keyboard = course_keyboard()
        
        geography_found = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Geography" in button.text:
                    geography_found = True
                    print(f"✅ Geography button in keyboard: '{button.text}' -> {button.callback_data}")
                    break
            if geography_found:
                break
        
        if not geography_found:
            print("❌ Geography not found in course keyboard!")
            return False
        
        # Test 4: List Geography chapters
        print("\n4️⃣ Geography chapters available:")
        for i, chapter in enumerate(chapters, 1):
            print(f"   {i:2d}. {chapter.name}")
        
        print(f"\n🎉 SUCCESS! Geography exam system is working!")
        print(f"📚 Total courses in system: {db.query(Course).count()}")
        print(f"📖 Total chapters for Geography: {len(chapters)}")
        print(f"✅ Users can now select Geography from exam menu")
        print(f"✅ Geography chapters will be listed when Geography is selected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_geography_in_exam_system()
    if success:
        print("\n🌍 GEOGRAPHY IS READY FOR EXAMS!")
    else:
        print("\n❌ Geography exam system has issues!")
