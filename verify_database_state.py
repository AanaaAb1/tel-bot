#!/usr/bin/env python3
"""
Direct verification script to show current database state
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Starting database verification...")
print("Current working directory:", os.getcwd())
print("Python path includes:", os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database.session import SessionLocal
    print("✓ Successfully imported SessionLocal")
    
    from app.models.course import Course
    print("✓ Successfully imported Course model")
    
    from app.models.chapter import Chapter
    print("✓ Successfully imported Chapter model")
    
    db = SessionLocal()
    print("✓ Successfully created database session")
    
    courses = db.query(Course).all()
    print(f"\n📊 Total courses found: {len(courses)}")
    
    if len(courses) == 0:
        print("❌ No courses found in database!")
    else:
        print("\n📋 Course Details:")
        for course in sorted(courses, key=lambda x: x.id):
            chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
            status = "✅" if chapters_count == 10 else "❌"
            print(f"   {status} {course.id:2d}. {course.name:<15} - {chapters_count:2d} chapters")
        
        # Check if all courses have 10 chapters
        all_have_10 = all(db.query(Chapter).filter_by(course_id=c.id).count() == 10 for c in courses)
        
        print(f"\n🎯 Final Status:")
        if all_have_10:
            print("🎉 SUCCESS: All courses have exactly 10 chapters!")
        else:
            print("❌ FAILED: Some courses don't have 10 chapters")
            
            # Show which courses need fixing
            print("\n📋 Courses needing chapters:")
            for course in courses:
                chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
                if chapters_count != 10:
                    print(f"   - {course.name}: {chapters_count} chapters (needs {10 - chapters_count} more)")
    
    db.close()
    print("\n✓ Database session closed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

