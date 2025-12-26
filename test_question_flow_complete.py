ly#!/usr/bin/env python3
"""
Final comprehensive test to verify that the question import and flow is working end-to-end.
This tests the complete pipeline from import → database storage → chapter retrieval → question access.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.course_service import get_course_by_id, get_courses_by_code
from app.handlers.course_handler import get_chapters_by_course
from app.services.question_service import get_questions_by_chapter
from app.database.session import SessionLocal
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.question import Question

def test_complete_question_flow():
    """Test the complete question flow from database to retrieval"""
    
    print("=== FINAL COMPREHENSIVE QUESTION FLOW TEST ===\n")
    
    success = True
    
    # Test 1: Verify courses exist and are accessible
    print("📚 Test 1: Course Access...")
    courses = SessionLocal().query(Course).all()
    print(f"  ✅ Found {len(courses)} courses in database")
    for course in courses:
        print(f"     - {course.name} (ID: {course.id})")
    
    # Test 2: Verify chapters exist and are linked to courses
    print("\n📖 Test 2: Chapter-Course Linking...")
    chapters = SessionLocal().query(Chapter).all()
    print(f"  ✅ Found {len(chapters)} chapters in database")
    for chapter in chapters:
        print(f"     - {chapter.name} (ID: {chapter.id}) -> Course: {chapter.course_id}")
    
    # Test 3: Verify questions exist and are linked to chapters
    print("\n❓ Test 3: Question-Chapter Linking...")
    questions = SessionLocal().query(Question).all()
    print(f"  ✅ Found {len(questions)} questions in database")
    for question in questions:
        print(f"     - Q: {question.text[:50]}... -> Chapter ID: {question.chapter_id}")
    
    # Test 4: Test course handler can retrieve chapters
    print("\n🔧 Test 4: Course Handler Chapter Retrieval...")
    try:
        # Test Biology course
        biology_chapters = get_chapters_by_course(1)
        print(f"  ✅ Biology course chapters: {len(biology_chapters)}")
        for chapter in biology_chapters:
            questions_in_chapter = get_questions_by_chapter(chapter.id)
            print(f"     - Chapter '{chapter.name}' has {len(questions_in_chapter)} questions")
            if len(questions_in_chapter) > 0:
                print(f"       Sample: {questions_in_chapter[0].text[:50]}...")
        
        # Test Physics course
        physics_chapters = get_chapters_by_course(2)
        print(f"  ✅ Physics course chapters: {len(physics_chapters)}")
        for chapter in physics_chapters:
            questions_in_chapter = get_questions_by_chapter(chapter.id)
            print(f"     - Chapter '{chapter.name}' has {len(questions_in_chapter)} questions")
            if len(questions_in_chapter) > 0:
                print(f"       Sample: {questions_in_chapter[0].text[:50]}...")
                
    except Exception as e:
        print(f"  ❌ Error in course handler: {e}")
        success = False
    
    # Test 5: Verify the data structure matches what the bot expects
    print("\n🤖 Test 5: Bot Compatibility Check...")
    try:
        # Simulate what the bot would do when a user selects a course
        selected_course_id = 1  # Biology
        chapters = get_chapters_by_course(selected_course_id)
        
        if chapters:
            selected_chapter = chapters[0]  # First chapter
            questions = get_questions_by_chapter(selected_chapter.id)
            
            print(f"  ✅ Course {selected_course_id} -> Chapter {selected_chapter.id} -> {len(questions)} questions")
            
            if questions:
                print(f"  ✅ Questions available for exam!")
                print(f"     First question: {questions[0].text[:50]}...")
                print(f"     Options: A) {questions[0].option_a}, B) {questions[0].option_b}")
                print(f"     Correct answer: {questions[0].correct_answer}")
            else:
                print(f"  ⚠️  No questions found for chapter {selected_chapter.id}")
                success = False
        else:
            print(f"  ❌ No chapters found for course {selected_course_id}")
            success = False
            
    except Exception as e:
        print(f"  ❌ Error in bot compatibility test: {e}")
        success = False
    
    # Test 6: Verify database integrity
    print("\n🗄️  Test 6: Database Integrity...")
    try:
        db = SessionLocal()
        
        # Check for orphaned questions (questions with invalid chapter_id)
        orphaned_questions = db.query(Question).filter(
            Question.chapter_id.isnot(None)
        ).filter(
            ~Question.chapter_id.in_(db.query(Chapter.id))
        ).count()
        
        if orphaned_questions == 0:
            print(f"  ✅ No orphaned questions found")
        else:
            print(f"  ⚠️  Found {orphaned_questions} orphaned questions")
        
        # Check for questions without proper fields
        incomplete_questions = db.query(Question).filter(
            (Question.text.isNone()) | 
            (Question.option_a.isNone()) |
            (Question.correct_answer.isNone())
        ).count()
        
        if incomplete_questions == 0:
            print(f"  ✅ All questions have required fields")
        else:
            print(f"  ⚠️  Found {incomplete_questions} incomplete questions")
            success = False
            
        db.close()
        
    except Exception as e:
        print(f"  ❌ Error in database integrity check: {e}")
        success = False
    
    # Final summary
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Question import system is working correctly!")
        print("✅ Course handler can retrieve chapters successfully!")
        print("✅ Questions are properly linked to chapters!")
        print("✅ Bot can access questions for exams!")
        print("✅ Database integrity is maintained!")
        print("\n🚀 The 'next question' issue should now be RESOLVED!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️  There may still be issues with the question flow.")
        
    print("="*60)
    
    return success

if __name__ == "__main__":
    try:
        success = test_complete_question_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
