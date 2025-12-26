#!/usr/bin/env python3
"""
Migration script to add chapters table and update questions table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database.session import SessionLocal
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.question import Question
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_chapters_table():
    """Create the chapters table"""
    try:
        # Get database connection
        db = SessionLocal()
        engine = db.bind
        
        # Create chapters table using raw SQL to avoid model dependency
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                name VARCHAR NOT NULL,
                description TEXT,
                order_index INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
        """))
        db.commit()
        
        logger.info("✅ Chapters table created successfully")
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating chapters table: {e}")
        return False

def add_chapter_id_to_questions():
    """Add chapter_id column to questions table if it doesn't exist"""
    try:
        db = SessionLocal()
        engine = db.bind
        
        # Check if chapter_id column exists using SQLite pragma
        with engine.connect() as conn:
            # Check for column existence in SQLite
            result = conn.execute(text("PRAGMA table_info(questions)"))
            columns = [row[1] for row in result.fetchall()]  # row[1] is column name
            
            if 'chapter_id' not in columns:
                # Add chapter_id column
                conn.execute(text("""
                    ALTER TABLE questions 
                    ADD COLUMN chapter_id INTEGER
                """))
                conn.commit()
                logger.info("✅ Added chapter_id column to questions table")
            else:
                logger.info("ℹ️ chapter_id column already exists in questions table")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding chapter_id column: {e}")
        return False

def seed_default_chapters():
    """Seed default chapters for existing courses"""
    try:
        db = SessionLocal()
        
        # Get all courses using raw SQL to avoid model issues
        result = db.execute(text("SELECT id, name FROM courses"))
        courses = result.fetchall()
        
        if not courses:
            logger.info("No courses found to create chapters for")
            db.close()
            return True
        
        default_chapters = [
            "Chapter 1: Introduction",
            "Chapter 2: Fundamentals", 
            "Chapter 3: Advanced Topics",
            "Chapter 4: Applications",
            "Chapter 5: Review and Practice"
        ]
        
        for course_row in courses:
            course_id = course_row[0]
            course_name = course_row[1]
            
            # Check if course already has chapters
            existing_chapters_result = db.execute(
                text("SELECT COUNT(*) FROM chapters WHERE course_id = :course_id"),
                {"course_id": course_id}
            )
            chapter_count = existing_chapters_result.scalar()
            
            if chapter_count == 0:
                logger.info(f"Creating default chapters for course: {course_name}")
                
                # Insert chapters using raw SQL
                for i, chapter_name in enumerate(default_chapters, 1):
                    db.execute(
                        text("""
                            INSERT INTO chapters (course_id, name, description, order_index)
                            VALUES (:course_id, :name, :description, :order_index)
                        """),
                        {
                            "course_id": course_id,
                            "name": chapter_name,
                            "description": f"Default chapter for {course_name}",
                            "order_index": i
                        }
                    )
                
                db.commit()
                logger.info(f"✅ Created {len(default_chapters)} default chapters for {course_name}")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error seeding default chapters: {e}")
        return False

def update_questions_without_chapter():
    """Update questions that don't have a chapter assigned"""
    try:
        db = SessionLocal()
        
        # Find questions without chapter_id using raw SQL
        result = db.execute(text("SELECT COUNT(*) FROM questions WHERE chapter_id IS NULL"))
        questions_count = result.scalar()
        
        if questions_count > 0:
            logger.info(f"Found {questions_count} questions without chapter assignment")
            
            # Get all courses using raw SQL
            courses_result = db.execute(text("SELECT id, name FROM courses"))
            courses = courses_result.fetchall()
            
            for course_row in courses:
                course_id = course_row[0]
                course_name = course_row[1]
                
                # Get the first chapter for this course
                chapter_result = db.execute(
                    text("SELECT id FROM chapters WHERE course_id = :course_id ORDER BY order_index LIMIT 1"),
                    {"course_id": course_id}
                )
                first_chapter = chapter_result.fetchone()
                
                if first_chapter:
                    chapter_id = first_chapter[0]
                    
                    # Update questions for this course to use the first chapter
                    update_result = db.execute(
                        text("UPDATE questions SET chapter_id = :chapter_id WHERE chapter_id IS NULL AND course = :course_name"),
                        {"chapter_id": chapter_id, "course_name": course_name}
                    )
                    
                    updated_count = update_result.rowcount
                    logger.info(f"Assigned {updated_count} questions to first chapter of {course_name}")
            
            db.commit()
            logger.info("✅ Updated questions without chapter assignment")
        else:
            logger.info("ℹ️ No questions found without chapter assignment")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating questions: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting chapters migration...")
    
    try:
        # Step 1: Create chapters table
        if not create_chapters_table():
            logger.error("Failed to create chapters table")
            return False
        
        # Step 2: Add chapter_id to questions table
        if not add_chapter_id_to_questions():
            logger.error("Failed to add chapter_id column")
            return False
        
        # Step 3: Seed default chapters
        if not seed_default_chapters():
            logger.error("Failed to seed default chapters")
            return False
        
        # Step 4: Update existing questions
        if not update_questions_without_chapter():
            logger.error("Failed to update existing questions")
            return False
        
        logger.info("✅ Chapters migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

