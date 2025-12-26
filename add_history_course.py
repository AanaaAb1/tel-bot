#!/usr/bin/env python3
"""
Script to add History course to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database.session import SessionLocal

def add_history_course():
    """Add History course to the database"""
    db = SessionLocal()

    try:
        # Check if History course already exists
        result = db.execute(text("SELECT id FROM courses WHERE name = 'History'"))
        existing_course = result.first()
        
        if existing_course:
            print("✅ History course already exists in database!")
            return existing_course[0]

        print("Adding History course to database...")

        # Add History course using raw SQL
        db.execute(
            text("INSERT INTO courses (name, description) VALUES (:name, :description)"),
            {
                "name": "History", 
                "description": "History course covering ancient civilizations, medieval history, modern history, and world history"
            }
        )

        db.commit()
        print("✅ History course added successfully!")

        # Get the course ID
        result = db.execute(text("SELECT id FROM courses WHERE name = 'History'"))
        course_id = result.scalar()
        print(f"History course ID: {course_id}")

        return course_id

    except Exception as e:
        db.rollback()
        print(f"❌ Error adding History course: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    course_id = add_history_course()
    if course_id:
        print(f"🎉 History course created with ID: {course_id}")
