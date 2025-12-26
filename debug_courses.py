#!/usr/bin/env python3
"""
Debug script to check courses and exams in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.exam import Exam
from app.services.course_service import get_course_by_name, get_all_courses

def debug_courses():
    """Debug course and exam data"""
    print("=== DEBUGGING COURSES AND EXAMS ===\n")
    
    # Check all courses
    print("1. All courses in database:")
    courses = get_all_courses()
    for course in courses:
        print(f"   ID: {course.id}, Name: '{course.name}', Description: '{course.description}'")
    
    print(f"\nTotal courses: {len(courses)}")
    
    # Check Biology specifically
    print("\n2. Checking Biology course:")
    biology_variations = ["Biology", "biology", "BIO", "Bio"]
    for variation in biology_variations:
        course = get_course_by_name(variation)
        if course:
            print(f"   Found: '{variation}' -> ID: {course.id}, Name: '{course.name}'")
            
            # Check exams for this course
            db = SessionLocal()
            exams = db.query(Exam).filter_by(course_id=course.id).all()
            db.close()
            
            print(f"   Exams for {course.name}:")
            if exams:
                for exam in exams:
                    print(f"     - ID: {exam.id}, Name: '{exam.name}'")
            else:
                print("     No exams found for this course!")
        else:
            print(f"   Not found: '{variation}'")
    
    # Check all exams
    print("\n3. All exams in database:")
    db = SessionLocal()
    all_exams = db.query(Exam).all()
    db.close()
    
    for exam in all_exams:
        print(f"   ID: {exam.id}, Name: '{exam.name}', Course ID: {exam.course_id}")
    
    print(f"\nTotal exams: {len(all_exams)}")
    
    # Check if there are any exams without course_id
    print("\n4. Exams without valid course_id:")
    db = SessionLocal()
    courses_dict = {c.id: c.name for c in courses}
    for exam in all_exams:
        course_name = courses_dict.get(exam.course_id, "UNKNOWN")
        print(f"   Exam '{exam.name}' -> Course: {course_name} (ID: {exam.course_id})")

if __name__ == "__main__":
    debug_courses()
