#!/usr/bin/env python3
"""
Debug script to check course and chapter data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models import Course, Chapter, Question

def debug_courses_chapters():
    db = SessionLocal()
    
    try:
        print("=== DEBUGGING COURSES AND CHAPTERS ===\n")
        
        # Check courses
        courses = db.query(Course).all()
        print(f"Total courses: {len(courses)}")
        
        if courses:
            for course in courses:
                print(f"\n--- Course: {course.name} (ID: {course.id}) ---")
                
                # Check chapters for this course
                chapters = db.query(Chapter).filter_by(course_id=course.id).all()
                print(f"Chapters found: {len(chapters)}")
                
                if chapters:
                    for chapter in chapters:
                        print(f"  - Chapter: {chapter.name} (ID: {chapter.id})")
                        
                        # Check questions for this chapter
                        questions = db.query(Question).filter_by(chapter_id=chapter.id).all()
                        print(f"    Questions: {len(questions)}")
                        
                        if questions:
                            print("    Sample question:")
                            sample_q = questions[0]
                            print(f"    '{sample_q.text[:50]}...'")
                else:
                    print("  ❌ No chapters found for this course!")
                    
        else:
            print("❌ No courses found in database!")
            
        # Check all chapters regardless of course
        print(f"\n=== ALL CHAPTERS IN DATABASE ===")
        all_chapters = db.query(Chapter).all()
        print(f"Total chapters: {len(all_chapters)}")
        
        for chapter in all_chapters:
            print(f"- {chapter.name} (Course ID: {chapter.course_id})")
            
        # Check all questions and their chapters
        print(f"\n=== ALL QUESTIONS AND THEIR CHAPTERS ===")
        all_questions = db.query(Question).all()
        print(f"Total questions: {len(all_questions)}")
        
        for q in all_questions:
            chapter = db.query(Chapter).filter_by(id=q.chapter_id).first()
            course_name = "Unknown"
            if chapter:
                course = db.query(Course).filter_by(id=chapter.course_id).first()
                if course:
                    course_name = course.name
                    
            print(f"- Q: '{q.text[:30]}...' -> Chapter: {chapter.name if chapter else 'None'} -> Course: {course_name}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_courses_chapters()
