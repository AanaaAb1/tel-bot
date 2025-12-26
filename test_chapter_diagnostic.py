#!/usr/bin/env python3
import sys
sys.path.append('/home/aneman/Desktop/Exambot/telegramexambot')

def test_chapter_selection_issues():
    print("🔍 DIAGNOSING CHAPTER SELECTION ISSUES")
    print("=" * 50)

    try:
        # Test 1: Check database connectivity and chapter existence
        from app.database.session import SessionLocal
        from app.models.course import Course
        from app.models.chapter import Chapter

        db = SessionLocal()
        
        # Get all courses
        courses = db.query(Course).all()
        print(f"📚 Total courses in database: {len(courses)}")
        
        if courses:
            for course in courses:
                print(f"   📖 Course: {course.name} (ID: {course.id})")
                
                # Check chapters for each course
                chapters = db.query(Chapter).filter_by(course_id=course.id).all()
                print(f"      📝 Chapters found: {len(chapters)}")
                
                if chapters:
                    for chapter in chapters:
                        print(f"         📄 {chapter.name} (ID: {chapter.id})")
                else:
                    print(f"         ⚠️ NO CHAPTERS FOUND for course {course.id}")
        else:
            print("❌ NO COURSES FOUND IN DATABASE!")
            
        db.close()
        
        # Test 2: Test chapter service functionality
        print(f"\n🧪 TESTING CHAPTER SERVICE...")
        from app.services.chapter_service import get_chapters_by_course
        
        if courses:
            test_course_id = courses[0].id
            print(f"Testing with course ID: {test_course_id}")
            
            chapters = get_chapters_by_course(test_course_id)
            print(f"get_chapters_by_course returned: {len(chapters)} chapters")
            
            if chapters:
                for chapter in chapters:
                    print(f"   ✅ Chapter: {chapter.name} (ID: {chapter.id})")
            else:
                print("   ❌ get_chapters_by_course returned empty list")
        
        # Test 3: Check callback patterns in course handler
        print(f"\n📱 CHECKING CALLBACK PATTERNS...")
        
        # Check if the course handler exists and is properly imported
        try:
            from app.handlers.course_handler import select_course
            print("✅ select_course function imported successfully")
        except Exception as e:
            print(f"❌ Failed to import select_course: {e}")
            
        # Test 4: Check dispatcher integration
        print(f"\n🔗 CHECKING DISPATCHER INTEGRATION...")
        
        # Check if the handler is registered in dispatcher
        try:
            from app.bot.dispatcher_fixed import app
            print("✅ Dispatcher imported successfully")
            
            # Check handler registrations (this is informational)
            print("ℹ️ Check handlers manually in dispatcher file")
            
        except Exception as e:
            print(f"❌ Failed to import dispatcher: {e}")
        
        # Test 5: Test adding a sample chapter if none exist
        print(f"\n🔧 CREATING SAMPLE CHAPTERS...")
        
        if courses and len(chapters) == 0:
            print("No chapters found. Creating sample chapters...")
            
            db = SessionLocal()
            try:
                from app.services.chapter_service import ChapterService
                
                chapter_service = ChapterService(db)
                
                # Create sample chapters for each course
                for course in courses:
                    print(f"Creating chapters for course: {course.name}")
                    
                    # Create sample chapters
                    sample_chapters = [
                        ("Chapter 1: Introduction", "Introduction to the subject"),
                        ("Chapter 2: Basics", "Fundamental concepts"),
                        ("Chapter 3: Advanced Topics", "Advanced material"),
                        ("Chapter 4: Practice", "Practice problems")
                    ]
                    
                    for i, (name, desc) in enumerate(sample_chapters, 1):
                        try:
                            chapter = chapter_service.create_chapter(
                                course_id=course.id,
                                name=name,
                                description=desc,
                                order_index=i
                            )
                            print(f"   ✅ Created: {name}")
                        except Exception as e:
                            print(f"   ❌ Failed to create {name}: {e}")
                
                db.commit()
                print("✅ Sample chapters created successfully!")
                
            except Exception as e:
                print(f"❌ Error creating sample chapters: {e}")
                db.rollback()
            finally:
                db.close()
        
        # Test 6: Verify chapters after creation
        print(f"\n🔍 VERIFYING CHAPTERS AFTER CREATION...")
        
        db = SessionLocal()
        try:
            courses = db.query(Course).all()
            total_chapters = 0
            
            for course in courses:
                chapters = db.query(Chapter).filter_by(course_id=course.id).all()
                total_chapters += len(chapters)
                print(f"📚 {course.name}: {len(chapters)} chapters")
                
            print(f"📊 Total chapters in database: {total_chapters}")
            
        finally:
            db.close()
        
        print(f"\n✅ CHAPTER SELECTION DIAGNOSTIC COMPLETE!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chapter_selection_issues()

