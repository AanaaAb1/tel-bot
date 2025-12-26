#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.exam import Exam

def create_chapters_for_all_courses():
    """Create 10 chapters for each course"""
    db = SessionLocal()
    
    try:
        courses = db.query(Course).all()
        
        # Define 10 simple numbered chapter names for all courses
        course_chapters = {
            "Physics": [
                "Chapter 1",
                "Chapter 2",
                "Chapter 3",
                "Chapter 4",
                "Chapter 5",
                "Chapter 6",
                "Chapter 7",
                "Chapter 8",
                "Chapter 9",
                "Chapter 10"
            ],
            "Chemistry": [
                "Chapter 1",
                "Chapter 2",
                "Chapter 3",
                "Chapter 4",
                "Chapter 5",
                "Chapter 6",
                "Chapter 7",
                "Chapter 8",
                "Chapter 9",
                "Chapter 10"
            ],
            "Biology": [
                "Chapter 1",
                "Chapter 2",
                "Chapter 3",
                "Chapter 4",
                "Chapter 5",
                "Chapter 6",
                "Chapter 7",
                "Chapter 8",
                "Chapter 9",
                "Chapter 10"
            ],
            "Mathematics": [
                "Chapter 1",
                "Chapter 2",
                "Chapter 3",
                "Chapter 4",
                "Chapter 5",
                "Chapter 6",
                "Chapter 7",
                "Chapter 8",
                "Chapter 9",
                "Chapter 10"
            ],
            "English": [
                "Chapter 1",
                "Chapter 2",
                "Chapter 3",
                "Chapter 4",
                "Chapter 5",
                "Chapter 6",
                "Chapter 7",
                "Chapter 8",
                "Chapter 9",
                "Chapter 10"
            ],
            "Geography": [
                "Chapter 1",
                "Chapter 2",
                "Chapter 3",
                "Chapter 4",
                "Chapter 5",
                "Chapter 6",
                "Chapter 7",
                "Chapter 8",
                "Chapter 9",
                "Chapter 10"
            ],
            "History": [
                "Chapter 1",
                "Chapter 2",
                "Chapter 3",
                "Chapter 4",
                "Chapter 5",
                "Chapter 6",
                "Chapter 7",
                "Chapter 8",
                "Chapter 9",
                "Chapter 10"
            ]
        }
        
        total_chapters_created = 0
        
        for course in courses:
            print(f"📚 Creating chapters for: {course.name}")
            
            # Check if course already has chapters
            existing_chapters = db.query(Exam).filter(Exam.course_id == course.id).all()
            if len(existing_chapters) >= 10:
                print(f"  ✅ Already has {len(existing_chapters)} chapters, skipping...")
                continue
            
            # Get chapter names for this course
            chapter_names = course_chapters.get(course.name, [])
            
            if not chapter_names:
                print(f"  ❌ No chapter definitions found for {course.name}")
                continue
            
            chapters_created = 0
            for i, chapter_name in enumerate(chapter_names, 1):
                # Check if chapter already exists
                existing = db.query(Exam).filter(
                    Exam.course_id == course.id,
                    Exam.name == chapter_name
                ).first()
                
                if existing:
                    print(f"    ⚠️  Chapter '{chapter_name}' already exists, skipping...")
                    continue
                
                # Create new chapter
                new_chapter = Exam(
                    name=chapter_name,
                    course_id=course.id,
                    time_limit=30,  # 30 minutes default
                    total_questions=10,  # 10 questions per chapter
                    total_marks=100  # 100 marks total
                )
                
                db.add(new_chapter)
                chapters_created += 1
                print(f"    ✅ Created: {chapter_name}")
            
            if chapters_created > 0:
                db.commit()
                total_chapters_created += chapters_created
                print(f"  🎉 Successfully created {chapters_created} chapters for {course.name}")
            else:
                print(f"  ℹ️  No new chapters created for {course.name}")
            print()
        
        print(f"🎊 SUMMARY: Created {total_chapters_created} new chapters total")
        
        # Verify final status
        print("\n📊 FINAL CHAPTER STATUS:")
        print("=" * 60)
        for course in courses:
            chapter_count = len(db.query(Exam).filter(Exam.course_id == course.id).all())
            status = "✅ COMPLETE" if chapter_count >= 10 else f"❌ NEEDS {10 - chapter_count} MORE"
            print(f"Course: {course.name:<20} | chapters: {chapter_count:2d}/10 | {status}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_chapters_for_all_courses()
