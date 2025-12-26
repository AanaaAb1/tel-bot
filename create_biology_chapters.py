#!/usr/bin/env python3
"""
Create additional chapters for Biology course to demonstrate
the complete chapter listing functionality with some chapters having no questions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.chapter import Chapter
from app.models.course import Course

def create_additional_biology_chapters():
    """Create additional chapters for Biology course"""
    
    print("🧬 Creating Additional Biology Chapters...")
    
    db = SessionLocal()
    try:
        # Get Biology course
        biology_course = db.query(Course).filter_by(id=1).first()
        if not biology_course:
            print("❌ Biology course not found!")
            return False
        
        print(f"📚 Found Biology course: {biology_course.name}")
        
        # Check existing chapters
        existing_chapters = db.query(Chapter).filter_by(course_id=1).all()
        print(f"📖 Existing Biology chapters: {len(existing_chapters)}")
        
        # Define additional chapters to create
        additional_chapters = [
            {"name": "Chapter 2", "description": "Cell Biology and Structure"},
            {"name": "Chapter 3", "description": "Genetics and Heredity"}, 
            {"name": "Chapter 4", "description": "Evolution and Natural Selection"},
            {"name": "Chapter 5", "description": "Ecology and Ecosystems"},
            {"name": "Chapter 6", "description": "Human Anatomy and Physiology"},
            {"name": "Chapter 7", "description": "Molecular Biology"},
            {"name": "Chapter 8", "description": "Plant Biology"},
            {"name": "Chapter 9", "description": "Animal Behavior"},
            {"name": "Chapter 10", "description": "Biotechnology Applications"}
        ]
        
        created_count = 0
        
        # Create each chapter
        for chapter_data in additional_chapters:
            chapter_name = chapter_data["name"]
            
            # Check if chapter already exists
            existing = db.query(Chapter).filter_by(
                course_id=1, 
                name=chapter_name
            ).first()
            
            if existing:
                print(f"  ⚠️  {chapter_name} already exists")
                continue
            
            # Create new chapter
            new_chapter = Chapter(
                name=chapter_name,
                description=chapter_data["description"],
                course_id=1
            )
            
            db.add(new_chapter)
            db.commit()
            db.refresh(new_chapter)
            
            print(f"  ✅ Created {chapter_name} (ID: {new_chapter.id})")
            created_count += 1
        
        # Get final count
        total_chapters = db.query(Chapter).filter_by(course_id=1).all()
        print(f"\n📊 Total Biology chapters after creation: {len(total_chapters)}")
        
        # List all chapters with question counts
        print(f"\n📚 Complete Biology Chapter List:")
        from app.services.question_service import get_questions_by_chapter
        
        for i, chapter in enumerate(sorted(total_chapters, key=lambda x: x.name), 1):
            questions_count = len(get_questions_by_chapter(chapter.id))
            status = "✅ Has questions" if questions_count > 0 else "❌ No questions"
            print(f"  {i:2d}. {chapter.name} (ID: {chapter.id}) -> {questions_count} questions -> {status}")
        
        print(f"\n🎉 Successfully created {created_count} new chapters for Biology!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating chapters: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_additional_biology_chapters()
    sys.exit(0 if success else 1)
