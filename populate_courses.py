#!/usr/bin/env python3
"""
Script to populate courses in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database.session import SessionLocal

def populate_courses():
    """Add courses to the database"""
    db = SessionLocal()

    try:
        # Check if courses already exist
        result = db.execute(text("SELECT COUNT(*) FROM courses"))
        course_count = result.scalar()

        if course_count > 0:
            print(f"Database already has {course_count} courses!")
            return

        print("Adding courses to database...")

        # Add courses using raw SQL
        courses = [
            ("Physics", "Physics course covering mechanics, thermodynamics, and electromagnetism"),
            ("Chemistry", "Chemistry course covering organic, inorganic, and physical chemistry"),
            ("Biology", "Biology course covering cellular biology, genetics, and ecology"),
            ("Mathematics", "Mathematics course covering algebra, calculus, and statistics"),
            ("English", "English course covering language and literature")
        ]

        for name, description in courses:
            db.execute(
                text("INSERT INTO courses (name, description) VALUES (:name, :description)"),
                {"name": name, "description": description}
            )

        db.commit()
        print("✅ Courses added successfully!")

        # Verify courses were added
        result = db.execute(text("SELECT id, name FROM courses"))
        courses_added = result.fetchall()
        print(f"Added courses: {courses_added}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error adding courses: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    populate_courses()
