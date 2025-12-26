#!/usr/bin/env python3
"""
Verification script to test Geography course setup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.exam import Exam
from app.services.course_service import get_courses_by_code

def verify_geography_setup():
    """Verify Geography course and chapters setup"""
    db = SessionLocal()
    
    try:
        print("🔍 VERIFYING GEOGRAPHY COURSE SETUP")
        print("=" * 50)
        
        # Check Geography course exists
        geography_course = db.query(Course).filter(Course.name == "Geography").first()
        
        if not geography_course:
            print("❌ Geography course not found in database!")
            return False
        
        print(f"✅ Geography course found: ID {geography_course.id}")
        print(f"   Description: {geography_course.description}")
        
        # Check chapters
        chapters = db.query(Exam).filter(Exam.course_id == geography_course.id).all()
        
        print(f"\n📚 CHAPTERS CHECK:")
        print(f"Total chapters found: {len(chapters)}")
        
        if len(chapters) < 10:
            print(f"❌ Only {len(chapters)} chapters found, expected 10!")
            return False
        
        print("✅ All 10 chapters created successfully!")
        
        # List all chapters
        print("\n📋 CHAPTER LIST:")
        for i, chapter in enumerate(chapters, 1):
            print(f"  {i:2d}. {chapter.name}")
        
        # Test course service lookup
        print(f"\n🔍 TESTING COURSE SERVICE:")
        courses_by_code = get_courses_by_code("geography")
        
        if not courses_by_code:
            print("❌ Course service cannot find Geography!")
            return False
        
        print(f"✅ Course service found {len(courses_by_code)} Geography course(s)")
        
        # Test direct course lookup
        print(f"\n🧪 TESTING DIRECT COURSE LOOKUP:")
        all_courses = db.query(Course).all()
        course_names = [c.name for c in all_courses]
        
        if "Geography" not in course_names:
            print("❌ Geography not in course list!")
            return False
        
        print(f"✅ Geography found in all courses list")
        print(f"📊 Total courses in database: {len(all_courses)}")
        print(f"   Courses: {', '.join(course_names)}")
        
        print("\n🎉 GEOGRAPHY COURSE SETUP VERIFICATION COMPLETE!")
        print("✅ All systems working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = verify_geography_setup()
    if success:
        print("\n🌍 Geography course is fully operational!")
    else:
        print("\n❌ Geography course setup has issues!")
