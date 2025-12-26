#!/usr/bin/env python3
"""
Script to add Geography course to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database.session import SessionLocal

def add_geography_course():
    """Add Geography course to the database"""
    db = SessionLocal()

    try:
        # Check if Geography course already exists
        result = db.execute(text("SELECT id FROM courses WHERE name = 'Geography'"))
        existing_course = result.first()
        
        if existing_course:
            print("✅ Geography course already exists in database!")
            return existing_course[0]

        print("Adding Geography course to database...")

        # Add Geography course using raw SQL
        db.execute(
            text("INSERT INTO courses (name, description) VALUES (:name, :description)"),
            {
                "name": "Geography", 
                "description": "Geography course covering physical geography, human geography, and environmental studies"
            }
        )

        db.commit()
        print("✅ Geography course added successfully!")

        # Get the course ID
        result = db.execute(text("SELECT id FROM courses WHERE name = 'Geography'"))
        course_id = result.scalar()
        print(f"Geography course ID: {course_id}")

        return course_id

    except Exception as e:
        db.rollback()
        print(f"❌ Error adding Geography course: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    course_id = add_geography_course()
    if course_id:
        print(f"🎉 Geography course created with ID: {course_id}")
