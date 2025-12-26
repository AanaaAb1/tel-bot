#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.exam import Exam

def update_chapters_to_numbered_format():
    """Update all existing chapters to numbered format: Chapter 1, Chapter 2, etc."""
    db = SessionLocal()
    
    try:
        courses = db.query(Course).all()
        total_updated = 0
        
        print("🔄 Updating all chapters to numbered format...")
        print("=" * 60)
        
        for course in courses:
            print(f"📚 Processing course: {course.name}")
            
            # Get all chapters for this course, ordered by creation date (or ID)
            chapters = db.query(Exam).filter(Exam.course_id == course.id).order_by(Exam.id).all()
            
            if not chapters:
                print(f"  ❌ No chapters found for {course.name}")
                continue
                
            print(f"  📖 Found {len(chapters)} chapters to update")
            
            # Update chapter names to numbered format
            chapters_updated = 0
            for i, chapter in enumerate(chapters, 1):
                new_name = f"Chapter {i}"
                old_name = chapter.name
                
                if old_name != new_name:
                    chapter.name = new_name
                    chapters_updated += 1
                    print(f"    🔄 {old_name} → {new_name}")
            
            if chapters_updated > 0:
                db.commit()
                total_updated += chapters_updated
                print(f"  ✅ Updated {chapters_updated} chapters for {course.name}")
            else:
                print(f"  ℹ️  All chapters already in correct format")
            print()
        
        print(f"🎊 SUMMARY: Updated {total_updated} chapters total")
        
        # Show final status
        print("\n📊 FINAL CHAPTER STATUS:")
        print("=" * 60)
        for course in courses:
            chapters = db.query(Exam).filter(Exam.course_id == course.id).order_by(Exam.name).all()
            if chapters:
                print(f"📚 {course.name}:")
                for chapter in chapters:
                    print(f"  📖 {chapter.name}")
            else:
                print(f"📚 {course.name}: No chapters")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_chapters_to_numbered_format()

