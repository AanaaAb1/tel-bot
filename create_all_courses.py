#!/usr/bin/env python3
"""
Create all missing courses to complete the exam system.
Currently only Biology and Physics exist - we need 8 more courses.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.chapter import Chapter

def create_all_missing_courses():
    """Create all missing courses with their chapters"""
    
    print("🎓 CREATING ALL MISSING COURSES")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Check existing courses
        existing_courses = db.query(Course).all()
        existing_names = [course.name for course in existing_courses]
        
        print(f"📊 Existing courses: {len(existing_courses)}")
        for course in existing_courses:
            print(f"   ✅ {course.name} (ID: {course.id})")
        
        # Define all courses that should exist
        all_expected_courses = [
            {
                "name": "Mathematics",
                "description": "Advanced mathematics covering algebra, calculus, geometry, and statistics",
                "code": "math",
                "chapters": ["Algebra", "Calculus", "Geometry", "Statistics", "Trigonometry", "Number Theory", "Discrete Math", "Linear Algebra", "Probability", "Applied Math"]
            },
            {
                "name": "Chemistry",
                "description": "General chemistry covering atomic structure, chemical bonding, and reactions",
                "code": "chem",
                "chapters": ["Atomic Structure", "Chemical Bonding", "Periodic Table", "Stoichiometry", "Acids and Bases", "Organic Chemistry", "Thermodynamics", "Kinetics", "Electrochemistry", "Analytical Chemistry"]
            },
            {
                "name": "English",
                "description": "English language and literature covering grammar, writing, and literary analysis",
                "code": "eng",
                "chapters": ["Grammar and Syntax", "Literature Analysis", "Creative Writing", "Poetry", "Drama", "Novel Study", "Essay Writing", "Vocabulary", "Rhetoric", "Communication Skills"]
            },
            {
                "name": "Geography",
                "description": "Physical and human geography covering landforms, climate, and population",
                "code": "geo",
                "chapters": ["Physical Geography", "Human Geography", "Climate and Weather", "Geology", "Population Studies", "Economic Geography", "Urban Geography", "Environmental Geography", "Cartography", "Regional Geography"]
            },
            {
                "name": "History",
                "description": "World history covering ancient civilizations to modern times",
                "code": "hist",
                "chapters": ["Ancient Civilizations", "Medieval Period", "Renaissance", "Industrial Revolution", "World Wars", "Cold War", "Modern History", "African History", "Asian History", "American History"]
            },
            {
                "name": "Government",
                "description": "Civics and government covering political systems and institutions",
                "code": "gov",
                "chapters": ["Political Systems", "Constitution", "Federal Government", "State and Local Government", "Elections", "Public Policy", "International Relations", "Civil Rights", "Public Administration", "Political Theory"]
            },
            {
                "name": "Economics",
                "description": "Microeconomics and macroeconomics covering supply, demand, and markets",
                "code": "econ",
                "chapters": ["Supply and Demand", "Market Structures", "Macroeconomics", "International Trade", "Money and Banking", "Economic Growth", "Labor Economics", "Public Finance", "Development Economics", "Business Economics"]
            },
           
              
        ]
        
        created_courses = 0
        created_chapters = 0
        
        # Create each missing course
        for course_data in all_expected_courses:
            course_name = course_data["name"]
            
            if course_name in existing_names:
                print(f"   ⚠️  {course_name} already exists")
                continue
            
            # Create new course
            new_course = Course(
                name=course_name,
                description=course_data["description"],
                code=course_data["code"]
            )
            
            db.add(new_course)
            db.commit()
            db.refresh(new_course)
            
            print(f"   ✅ Created {course_name} (ID: {new_course.id})")
            created_courses += 1
            
            # Create chapters for this course
            for i, chapter_name in enumerate(course_data["chapters"], 1):
                new_chapter = Chapter(
                    name=f"Chapter {i}: {chapter_name}",
                    description=f"Comprehensive study of {chapter_name}",
                    course_id=new_course.id
                )
                db.add(new_chapter)
                created_chapters += 1
            
            db.commit()
            print(f"      📖 Added {len(course_data['chapters'])} chapters")
        
        # Get final counts
        total_courses = db.query(Course).all()
        total_chapters = db.query(Chapter).all()
        
        print(f"\n📊 FINAL DATABASE STATUS:")
        print(f"📚 Total courses: {len(total_courses)}")
        print(f"📖 Total chapters: {len(total_chapters)}")
        
        print(f"\n🎯 COMPLETE COURSE LIST:")
        for course in sorted(total_courses, key=lambda x: x.id):
            chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
            print(f"   {course.id:2d}. {course.name:<12} - {chapters_count} chapters")
        
        print(f"\n🎉 Successfully created {created_courses} new courses!")
        print(f"📚 Total courses now available: {len(total_courses)}/10")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating courses: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_all_missing_courses()
    sys.exit(0 if success else 1)
