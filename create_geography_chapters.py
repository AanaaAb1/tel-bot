#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.exam import Exam

def create_geography_chapters():
    """Create 10 Geography chapters (exams)"""
    db = SessionLocal()
    
    try:
        # Get Geography course
        geography_course = db.query(Course).filter(Course.name == "Geography").first()
        
        if not geography_course:
            print("❌ Geography course not found! Please run add_geography_course.py first.")
            return False
        
        print(f"📚 Creating chapters for: {geography_course.name}")
        
        # Check if Geography already has chapters
        existing_chapters = db.query(Exam).filter(Exam.course_id == geography_course.id).all()
        if len(existing_chapters) >= 10:
            print(f"  ✅ Already has {len(existing_chapters)} chapters, skipping...")
            return True
        
        # Define 10 Geography chapters
        geography_chapters = [
            "Introduction to Physical Geography",
            "Earth Structure and Plate Tectonics", 
            "Weather and Climate Systems",
            "Landforms and Geomorphology",
            "Hydrology and Water Resources",
            "Population Geography",
            "Settlement and Urban Geography", 
            "Economic Geography",
            "Cultural and Political Geography",
            "Environmental Geography and Conservation"
        ]
        
        chapters_created = 0
        for i, chapter_name in enumerate(geography_chapters, 1):
            # Check if chapter already exists
            existing = db.query(Exam).filter(
                Exam.course_id == geography_course.id,
                Exam.name == chapter_name
            ).first()
            
            if existing:
                print(f"    ⚠️  Chapter '{chapter_name}' already exists, skipping...")
                continue
            
            # Create new chapter
            new_chapter = Exam(
                name=chapter_name,
                course_id=geography_course.id,
                time_limit=30,  # 30 minutes default
                total_questions=10,  # 10 questions per chapter
                total_marks=100  # 100 marks total
            )
            
            db.add(new_chapter)
            chapters_created += 1
            print(f"    ✅ Created: {chapter_name}")
        
        if chapters_created > 0:
            db.commit()
            print(f"  🎉 Successfully created {chapters_created} chapters for Geography")
        else:
            print(f"  ℹ️  No new chapters created for Geography")
        
        # Verify final status
        final_chapters = db.query(Exam).filter(Exam.course_id == geography_course.id).all()
        print(f"\n📊 FINAL GEOGRAPHY STATUS:")
        print("=" * 60)
        print(f"Course: {geography_course.name:<20} | chapters: {len(final_chapters):2d}/10 | {'✅ COMPLETE' if len(final_chapters) >= 10 else '❌ INCOMPLETE'}")
        
        if len(final_chapters) >= 10:
            print("\n🎊 Geography course setup complete!")
            return True
        else:
            print(f"\n❌ Still need {10 - len(final_chapters)} more chapters")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_geography_chapters()
    if success:
        print("\n🌍 Geography course is ready for use!")
    else:
        print("\n❌ Geography course setup failed!")
