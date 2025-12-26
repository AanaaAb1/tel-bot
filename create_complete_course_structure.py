
#!/usr/bin/env python3
"""
Complete Course and Chapter Creation Script
Creates all missing courses with 10 chapters each
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.chapter import Chapter

def create_all_missing_courses():
    """Create all missing courses with chapters"""
    db = SessionLocal()
    
    try:
        # Get existing courses
        existing_courses = db.query(Course).all()
        existing_names = [course.name for course in existing_courses]
        
        print("📊 Current database state:")
        for course in sorted(existing_courses, key=lambda x: x.id):
            chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
            print(f"   {course.id:2d}. {course.name:<15} - {chapters_count:2d} chapters")
        
        print()
        
        # Define all courses that should exist
        courses_to_create = [
            {"name": "Mathematics", "description": "Mathematics course", "code": "math"},
            {"name": "Physics", "description": "Physics course", "code": "phys"},
            {"name": "Chemistry", "description": "Chemistry course", "code": "chem"},
            {"name": "Biology", "description": "Biology course", "code": "bio"},
            {"name": "English", "description": "English course", "code": "eng"},
            {"name": "Geography", "description": "Geography course", "code": "geo"},
            {"name": "History", "description": "History course", "code": "hist"},
            {"name": "Government", "description": "Government course", "code": "gov"},
            {"name": "Economics", "description": "Economics course", "code": "econ"},
            {"name": "Literature", "description": "Literature course", "code": "lit"}
        ]
        
        # Create missing courses
        created_courses = []
        for course_data in courses_to_create:
            if course_data["name"] not in existing_names:
                new_course = Course(
                    name=course_data["name"],
                    description=course_data["description"],
                    code=course_data["code"]
                )
                db.add(new_course)
                created_courses.append(new_course)
                print(f"✅ Created course: {course_data['name']}")
            else:
                print(f"ℹ️  Course already exists: {course_data['name']}")
        
        # Commit new courses
        if created_courses:
            db.commit()
            print(f"💾 Committed {len(created_courses)} new courses")
        
        print()
        
        # Get all courses after creation
        all_courses = db.query(Course).all()
        
        # Ensure each course has exactly 10 chapters
        for course in all_courses:
            existing_chapters = db.query(Chapter).filter_by(course_id=course.id).all()
            chapters_count = len(existing_chapters)
            
            if chapters_count < 10:
                print(f"📖 {course.name}: {chapters_count} chapters → creating {10 - chapters_count} more")
                
                # Create missing chapters
                for i in range(chapters_count + 1, 11):
                    new_chapter = Chapter(
                        name=f"Chapter {i}",
                        description=f"Chapter {i}",
                        course_id=course.id
                    )
                    db.add(new_chapter)
            elif chapters_count == 10:
                print(f"✅ {course.name}: {chapters_count} chapters (complete)")
            else:
                print(f"⚠️  {course.name}: {chapters_count} chapters (too many, keeping existing)")
        
        # Commit all chapter additions
        db.commit()
        print()
        
        # Final verification
        print("📋 Final database state:")
        total_courses = db.query(Course).all()
        total_chapters = 0
        
        for course in sorted(total_courses, key=lambda x: x.id):
            chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
            total_chapters += chapters_count
            status = "✅" if chapters_count == 10 else "❌"
            print(f"   {status} {course.id:2d}. {course.name:<15} - {chapters_count:2d} chapters")
        
        print()
        print(f"📊 Summary: {len(total_courses)} courses, {total_chapters} total chapters")
        
        # Check if all courses have 10 chapters
        incomplete_courses = []
        for course in total_courses:
            chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
            if chapters_count != 10:
                incomplete_courses.append(course.name)
        
        if incomplete_courses:
            print(f"❌ Courses with incorrect chapter count: {', '.join(incomplete_courses)}")
            return False
        else:
            print("✅ All courses have exactly 10 chapters!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting complete course and chapter creation...")
    print("=" * 60)
    
    success = create_all_missing_courses()
    
    print("=" * 60)
    if success:
        print("🎉 All courses and chapters created successfully!")
    else:
        print("⚠️  Some issues occurred during creation.")

