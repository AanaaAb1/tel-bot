#!/usr/bin/env python3
"""
Test script to verify questions are imported and accessible
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models import Course, Chapter, Question

def test_question_import():
    db = SessionLocal()
    
    try:
        print("Testing question import and access...")
        
        # Check if courses exist
        courses = db.query(Course).all()
        print(f"Courses found: {len(courses)}")
        for course in courses:
            print(f"  - {course.name}")
        
        # Check if chapters exist
        chapters = db.query(Chapter).all()
        print(f"Chapters found: {len(chapters)}")
        for chapter in chapters:
            print(f"  - {chapter.name} (Course: {chapter.course.name})")
        
        # Check if questions exist
        questions = db.query(Question).all()
        print(f"Questions found: {len(questions)}")
        
        if questions:
            print("Sample questions:")
            for i, q in enumerate(questions[:3]):
                print(f"  {i+1}. {q.text[:60]}...")
                print(f"     Answer: {q.correct_answer}")
                print(f"     Chapter: {q.chapter.name}")
                print(f"     Course: {q.course}")
                print()
            
            # Test question retrieval by chapter
            first_chapter = questions[0].chapter
            chapter_questions = db.query(Question).filter_by(chapter_id=first_chapter.id).all()
            print(f"Questions in chapter '{first_chapter.name}': {len(chapter_questions)}")
            
            return True
        else:
            print("❌ No questions found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_question_import()
    if success:
        print("✅ Question import test PASSED")
    else:
        print("❌ Question import test FAILED")
