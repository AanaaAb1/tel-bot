#!/usr/bin/env python3
"""
Simple script to check what courses exist in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course

def check_all_courses():
    """Check all courses in database"""
    print("🔍 CHECKING ALL COURSES IN DATABASE")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        print(f"📊 Total courses found: {len(courses)}")
        print()
        
        course_codes = []
        for course in courses:
            print(f"ID: {course.id}, Name: '{course.name}'")
            # Generate potential course codes
            code = course.name.lower().replace(' ', '')
            course_codes.append(f"'{code}': '{course.name}'")
        
        print("\n" + "=" * 50)
        print("📝 SUGGESTED CODE MAPPINGS:")
        print("=" * 50)
        for code_mapping in course_codes:
            print(f"        {code_mapping},")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_all_courses()
