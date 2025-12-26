#!/usr/bin/env python3
"""
Debug script to check all courses in the database and their callback data formats.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course

def debug_all_courses():
    """Check all courses in database and their properties"""
    print("🔍 DEBUGGING ALL COURSES IN DATABASE")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        print(f"📊 Total courses found: {len(courses)}")
        print()
        
        for i, course in enumerate(courses, 1):
            print(f"{i}. Course ID: {course.id}")
            print(f"   Name: {course.name}")
            print(f"   Description: {course.description}")
            print(f"   Stream: {getattr(course, 'stream', 'N/A')}")
            
            # Check what callback data this would generate
            callback_data = f"exam_course_{course.name.lower()}"
            print(f"   Expected callback: exam_course_{course.name.lower()}")
            print(f"   Numeric callback: exam_course_{course.id}")
            print()
        
        return courses
        
    finally:
        db.close()

def test_callback_data():
    """Test what callback data would be generated for course names"""
    print("🧪 TESTING CALLBACK DATA GENERATION")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        
        for course in courses:
            # Test different callback formats
            name_based = f"exam_course_{course.name.lower().replace(' ', '_')}"
            id_based = f"exam_course_{course.id}"
            
            print(f"Course: {course.name}")
            print(f"  Name-based callback: {name_based}")
            print(f"  ID-based callback: {id_based}")
            print()
            
    finally:
        db.close()

if __name__ == "__main__":
    courses = debug_all_courses()
    test_callback_data()
