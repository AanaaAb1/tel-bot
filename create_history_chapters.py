#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.exam import Exam

def create_history_chapters():
    """Create 10 History chapters (exams)"""
    db = SessionLocal()
    
    try:
        # Get History course
        history_course = db.query(Course).filter(Course.name == "History").first()
        
        if not history_course:
            print("❌ History course not found! Please run add_history_course.py first.")
            return False
        
        print(f"📚 Creating chapters for: {history_course.name}")
        
        # Check if History already has chapters
        existing_chapters = db.query(Exam).filter(Exam.course_id == history_course.id).all()
        if len(existing_chapters) >= 10:
            print(f"  ✅ Already has {len(existing_chapters)} chapters, skipping...")
            return True
        
        # Define 10 History chapters
        history_chapters = [
            "Ancient Civilizations",
            "Medieval History and the Middle Ages",
            "Renaissance and Reformation",
            "Industrial Revolution and Modernization",
            "World War I and Its Aftermath",
            "World War II and Global Conflicts",
            "Cold War and Decolonization",
            "Modern World History",
            "African and Asian History",
            "Contemporary Global History"
        ]
        
        chapters_created = 0
        for i, chapter_name in enumerate(history_chapters, 1):
            # Check if chapter already exists
            existing = db.query(Exam).filter(
                Exam.course_id == history_course.id,
                Exam.name == chapter_name
            ).first()
            
            if existing:
                print(f"    ⚠️  Chapter '{chapter_name}' already exists, skipping...")
                continue
            
            # Create new chapter
            new_chapter = Exam(
                name=chapter_name,
                course_id=history_course.id,
                time_limit=30,  # 30 minutes default
                total_questions=10,  # 10 questions per chapter
                total_marks=100  # 100 marks total
            )
            
            db.add(new_chapter)
            chapters_created += 1
            print(f"    ✅ Created: {chapter_name}")
        
        if chapters_created > 0:
            db.commit()
            print(f"  🎉 Successfully created {chapters_created} chapters for History")
        else:
            print(f"  ℹ️  No new chapters created for History")
        
        # Verify final status
        final_chapters = db.query(Exam).filter(Exam.course_id == history_course.id).all()
        print(f"\n📊 FINAL HISTORY STATUS:")
        print("=" * 60)
        print(f"Course: {history_course.name:<20} | chapters: {len(final_chapters):2d}/10 | {'✅ COMPLETE' if len(final_chapters) >= 10 else '❌ INCOMPLETE'}")
        
        if len(final_chapters) >= 10:
            print("\n🎊 History course setup complete!")
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
    success = create_history_chapters()
    if success:
        print("\n📜 History course is ready for use!")
    else:
        print("\n❌ History course setup failed!")
