#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.exam import Exam

def check_course_chapters():
    """Check how many chapters each course currently has"""
    db = SessionLocal()
    
    try:
        courses = db.query(Course).all()
        
        print("📚 CURRENT COURSE CHAPTER STATUS:")
        print("=" * 60)
        
        for course in courses:
            chapters = db.query(Exam).filter(Exam.course_id == course.id).all()
            chapter_count = len(chapters)
            print(f"Course: {course.name:<20} | chapters: {chapter_count:2d}/10")
            if chapter_count > 0:
                for chapter in chapters:
                    print(f"  - {chapter.name}")
            print()
        
        # Summary
        total_courses = len(courses)
        complete_courses = sum(1 for course in courses 
                             if len(db.query(Exam).filter(Exam.course_id == course.id).all()) >= 10)
        
        print(f"📊 SUMMARY:")
        print(f"Total courses: {total_courses}")
        print(f"Courses with 10+ chapters: {complete_courses}")
        print(f"Courses needing chapters: {total_courses - complete_courses}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_course_chapters()
