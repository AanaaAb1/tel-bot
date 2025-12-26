#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE COURSE CHAPTER IMPLEMENTATION
This script ensures ALL courses have exactly 10 chapters.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal, engine
from app.models.course import Course, Base
from app.models.chapter import Chapter
from app.models.user import User
from app.models.payment import Payment
from app.models.exam_session import ExamSession

def create_database_if_not_exists():
    """Create all database tables if they don't exist"""
    print("🔧 Creating database tables if needed...")
    try:
        Base.metadata.create_all(engine)
        print("✅ Database tables created/verified")
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_all_courses():
    """Create all expected courses if they don't exist"""
    print("\n📚 Creating/Verifying all courses...")
    
    # Define all expected courses
    expected_courses = [
        {"name": "Mathematics", "code": "math", "description": "Mathematics course"},
        {"name": "Physics", "code": "phys", "description": "Physics course"},
        {"name": "Chemistry", "code": "chem", "description": "Chemistry course"},
        {"name": "Biology", "code": "bio", "description": "Biology course"},
        {"name": "English", "code": "eng", "description": "English course"},
        {"name": "Geography", "code": "geo", "description": "Geography course"},
        {"name": "History", "code": "hist", "description": "History course"},
        {"name": "Government", "code": "gov", "description": "Government course"},
        {"name": "Economics", "code": "econ", "description": "Economics course"},
        {"name": "Literature", "code": "lit", "description": "Literature course"}
    ]
    
    db = SessionLocal()
    try:
        created_count = 0
        
        for course_data in expected_courses:
            # Check if course already exists
            existing_course = db.query(Course).filter_by(name=course_data["name"]).first()
            
            if not existing_course:
                # Create new course
                new_course = Course(
                    name=course_data["name"],
                    code=course_data["code"],
                    description=course_data["description"]
                )
                db.add(new_course)
                created_count += 1
                print(f"   ✅ Created course: {course_data['name']}")
            else:
                print(f"   ✅ Course already exists: {course_data['name']}")
        
        if created_count > 0:
            db.commit()
            print(f"✅ {created_count} new courses created")
        else:
            print("✅ All courses already exist")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating courses: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_chapters_for_all_courses():
    """Create exactly 10 chapters for each course"""
    print("\n📖 Creating 10 chapters for each course...")
    
    db = SessionLocal()
    try:
        # Get all courses
        courses = db.query(Course).all()
        total_chapters_created = 0
        
        for course in courses:
            # Check how many chapters this course already has
            existing_chapters = db.query(Chapter).filter_by(course_id=course.id).all()
            chapters_count = len(existing_chapters)
            
            if chapters_count == 10:
                print(f"   ✅ {course.name}: Already has 10 chapters")
                continue
            elif chapters_count > 10:
                print(f"   ⚠️  {course.name}: Has {chapters_count} chapters (more than expected)")
                continue
            
            # Create missing chapters
            chapters_to_create = 10 - chapters_count
            
            for i in range(chapters_to_create):
                chapter_number = chapters_count + i + 1
                
                # Check if chapter with this number already exists
                existing_chapter = db.query(Chapter).filter_by(
                    course_id=course.id, 
                    name=f"Chapter {chapter_number}"
                ).first()
                
                if not existing_chapter:
                    new_chapter = Chapter(
                        name=f"Chapter {chapter_number}",
                        description=f"{course.name} - Chapter {chapter_number}",
                        course_id=course.id
                    )
                    db.add(new_chapter)
                    total_chapters_created += 1
            
            print(f"   ✅ {course.name}: Added {chapters_to_create} chapters")
        
        if total_chapters_created > 0:
            db.commit()
            print(f"✅ {total_chapters_created} total chapters created")
        else:
            print("✅ All courses already have 10 chapters")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating chapters: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def verify_final_state():
    """Verify that all courses have exactly 10 chapters"""
    print("\n🔍 Final Verification - Checking all courses...")
    
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        print(f"📊 Total courses found: {len(courses)}")
        
        if len(courses) == 0:
            print("❌ No courses found in database!")
            return False
        
        all_good = True
        print("\n📋 Course Status:")
        
        for course in sorted(courses, key=lambda x: x.id):
            chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
            status = "✅" if chapters_count == 10 else "❌"
            print(f"   {status} {course.id:2d}. {course.name:<15} - {chapters_count:2d} chapters")
            
            if chapters_count != 10:
                all_good = False
        
        print(f"\n🎯 Final Result:")
        if all_good:
            print("🎉 SUCCESS: All courses have exactly 10 chapters!")
            print("🚀 The bot is ready - users can click any course to see its chapters!")
        else:
            print("❌ FAILED: Some courses don't have 10 chapters")
            print("   This should not happen - please check the implementation")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    finally:
        db.close()

def main():
    """Main execution function"""
    print("🚀 COMPREHENSIVE COURSE CHAPTER IMPLEMENTATION")
    print("=" * 60)
    
    # Step 1: Create database if needed
    if not create_database_if_not_exists():
        print("❌ Failed to create database")
        return False
    
    # Step 2: Create all courses
    if not create_all_courses():
        print("❌ Failed to create courses")
        return False
    
    # Step 3: Create chapters for all courses
    if not create_chapters_for_all_courses():
        print("❌ Failed to create chapters")
        return False
    
    # Step 4: Verify final state
    success = verify_final_state()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TASK COMPLETED SUCCESSFULLY!")
        print("✅ All courses now have 10 chapters")
        print("✅ Users can click any course to see chapter selection")
        print("✅ The chapters button functionality is working for ALL courses")
    else:
        print("❌ TASK FAILED!")
        print("Some issues remain - please check the output above")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

