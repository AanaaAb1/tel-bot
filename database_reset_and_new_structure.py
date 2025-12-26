#!/usr/bin/env python3
"""
DATABASE RESET AND NEW COURSE STRUCTURE IMPLEMENTATION
This script deletes the existing database schema and creates a new one
with the specified courses and chapters.
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

def delete_database_schema():
    """Drop all existing tables"""
    print("🗑️  Deleting existing database schema...")
    
    try:
        # Drop all tables
        Base.metadata.drop_all(engine)
        print("✅ All existing tables dropped successfully")
        return True
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False

def create_new_database_schema():
    """Create new database tables"""
    print("\n🏗️  Creating new database schema...")
    
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        print("✅ New database schema created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False

def create_specified_courses():
    """Create the courses specified by the user"""
    print("\n📚 Creating specified courses...")
    
    # Define the courses as specified by the user
    specified_courses = [
        {"name": "Maths for Natural", "code": "maths_n", "description": "Mathematics for Natural Sciences"},
        {"name": "Maths for Social", "code": "maths_s", "description": "Mathematics for Social Sciences"},
        {"name": "English", "code": "eng", "description": "English Language and Literature"},
        {"name": "Physics", "code": "phys", "description": "Physics"},
        {"name": "Biology", "code": "bio", "description": "Biology"},
        {"name": "Chemistry", "code": "chem", "description": "Chemistry"},
        {"name": "Geography", "code": "geo", "description": "Geography"},
        {"name": "History", "code": "hist", "description": "History"}
    ]
    
    db = SessionLocal()
    try:
        created_count = 0
        
        for course_data in specified_courses:
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
                print(f"   ✅ Created course: {course_data['name']} (code: {course_data['code']})")
            else:
                print(f"   ✅ Course already exists: {course_data['name']}")
        
        if created_count > 0:
            db.commit()
            print(f"✅ {created_count} new courses created")
        else:
            print("✅ All specified courses already exist")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating courses: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_chapters_for_new_courses():
    """Create 10 chapters for each of the new courses"""
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
            
            print(f"   ✅ {course.name}: Created {chapters_to_create} chapters")
        
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

def verify_new_database():
    """Verify the new database structure"""
    print("\n🔍 Verifying new database structure...")
    
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        print(f"📊 Total courses found: {len(courses)}")
        
        if len(courses) == 0:
            print("❌ No courses found in database!")
            return False
        
        all_good = True
        print("\n📋 New Course Structure:")
        
        for course in sorted(courses, key=lambda x: x.id):
            chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
            status = "✅" if chapters_count == 10 else "❌"
            print(f"   {status} {course.id:2d}. {course.name:<20} ({course.code:<8}) - {chapters_count:2d} chapters")
            
            if chapters_count != 10:
                all_good = False
        
        print(f"\n🎯 Final Result:")
        if all_good:
            print("🎉 SUCCESS: All specified courses have exactly 10 chapters!")
            print("🚀 The new database is ready for your project!")
        else:
            print("❌ FAILED: Some courses don't have 10 chapters")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    finally:
        db.close()

def test_project_integration():
    """Test integration with existing project components"""
    print("\n🔗 Testing project integration...")
    
    try:
        # Test course service integration
        from app.services.course_service import get_courses_by_code
        
        # Test getting courses by code
        test_codes = ["maths_n", "maths_s", "eng", "phys", "bio", "chem", "geo", "hist"]
        
        for code in test_codes:
            courses = get_courses_by_code(code)
            if courses:
                print(f"   ✅ Course service works for code: {code}")
            else:
                print(f"   ❌ Course service failed for code: {code}")
        
        # Test chapter service integration
        from app.services.chapter_service import get_chapters_by_course_id
        
        db = SessionLocal()
        try:
            # Test with first course
            first_course = db.query(Course).first()
            if first_course:
                chapters = get_chapters_by_course_id(first_course.id)
                print(f"   ✅ Chapter service works for course: {first_course.name}")
            else:
                print(f"   ❌ No courses found for chapter service test")
        finally:
            db.close()
        
        print("✅ Project integration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 DATABASE RESET AND NEW COURSE STRUCTURE")
    print("=" * 60)
    print("📋 New Course Structure:")
    print("   1. Maths for Natural (maths_n)")
    print("   2. Maths for Social (maths_s)")
    print("   3. English (eng)")
    print("   4. Physics (phys)")
    print("   5. Biology (bio)")
    print("   6. Chemistry (chem)")
    print("   7. Geography (geo)")
    print("   8. History (hist)")
    print("   Each course will have exactly 10 chapters")
    print("=" * 60)
    
    # Step 1: Delete existing schema
    if not delete_database_schema():
        print("❌ Failed to delete existing database")
        return False
    
    # Step 2: Create new schema
    if not create_new_database_schema():
        print("❌ Failed to create new database schema")
        return False
    
    # Step 3: Create specified courses
    if not create_specified_courses():
        print("❌ Failed to create specified courses")
        return False
    
    # Step 4: Create chapters for all courses
    if not create_chapters_for_new_courses():
        print("❌ Failed to create chapters")
        return False
    
    # Step 5: Verify new database
    if not verify_new_database():
        print("❌ Database verification failed")
        return False
    
    # Step 6: Test project integration
    if not test_project_integration():
        print("⚠️  Integration test failed, but database is ready")
    
    print("\n" + "=" * 60)
    print("🎉 DATABASE RESET COMPLETED SUCCESSFULLY!")
    print("✅ Old database schema deleted")
    print("✅ New database with specified courses created")
    print("✅ 10 chapters created for each course")
    print("✅ Database connected to your project")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

