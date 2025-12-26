#!/usr/bin/env python3
"""
Simple database check script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.chapter import Chapter

def main():
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        print(f"📊 Total courses: {len(courses)}")
        print()
        
        for course in sorted(courses, key=lambda x: x.id):
            chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
            print(f"{course.id}. {course.name:<15} - {chapters_count} chapters")
        
        return courses
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
