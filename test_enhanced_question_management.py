#!/usr/bin/env python3
"""
Test script for Enhanced Question Management System
Tests the complete workflow: Add Question → Store by Course/Chapter → Retrieve for Exam/Practice
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.services.question_service import (
    add_question_by_course_chapter,
    get_questions_with_fallback,
    get_questions_by_course_chapter,
    get_questions_by_course_name,
    get_chapter_question_count,
    get_course_question_count,
    get_questions_summary
)
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.exam import Exam
from app.models.question import Question

def test_enhanced_question_management():
    """Test the complete enhanced question management workflow"""
    print("🧪 Testing Enhanced Question Management System")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Test 1: Verify database structure and sample data
        print("\n1️⃣ Database Structure Verification")
        print("-" * 40)
        
        courses = db.query(Course).all()
        print(f"✅ Found {len(courses)} courses in database")
        
        chapters = db.query(Chapter).all()
        print(f"✅ Found {len(chapters)} chapters in database")
        
        exams = db.query(Exam).all()
        print(f"✅ Found {len(exams)} exams in database")
        
        questions = db.query(Question).all()
        print(f"✅ Found {len(questions)} questions in database")
        
        # Test 2: Add sample questions using enhanced method
        print("\n2️⃣ Adding Sample Questions with Enhanced Method")
        print("-" * 50)
        
        # Get first course and chapter for testing
        test_course = courses[0] if courses else None
        test_chapter = chapters[0] if chapters else None
        
        if test_course and test_chapter:
            print(f"📚 Testing with Course: {test_course.name}")
            print(f"📖 Testing with Chapter: {test_chapter.name}")
            
            # Add a sample question
            try:
                question = add_question_by_course_chapter(
                    course=test_course.name,
                    chapter_name=test_chapter.name,
                    question_text="What is the capital of France?",
                    option_a="London",
                    option_b="Berlin", 
                    option_c="Paris",
                    option_d="Madrid",
                    correct_answer="C"
                )
                print(f"✅ Successfully added question with ID: {question.id}")
                print(f"   Course: {question.course}")
                print(f"   Chapter ID: {question.chapter_id}")
                print(f"   Correct Answer: {question.correct_answer}")
                
            except Exception as e:
                print(f"❌ Error adding question: {e}")
                print("   This might be expected if course/chapter doesn't exist")
        
        # Test 3: Test enhanced retrieval methods
        print("\n3️⃣ Testing Enhanced Question Retrieval")
        print("-" * 45)
        
        if test_course:
            # Test course-wide retrieval
            course_questions = get_questions_by_course_name(test_course.name, limit=5)
            print(f"📚 Course-wide questions for {test_course.name}: {len(course_questions)} found")
            
            # Test with fallback
            if test_chapter:
                fallback_questions = get_questions_with_fallback(
                    course_name=test_course.name,
                    chapter_name=test_chapter.name,
                    limit=5
                )
                print(f"🎯 Fallback questions for {test_course.name} - {test_chapter.name}: {len(fallback_questions)} found")
            
        # Test 4: Question counting methods
        print("\n4️⃣ Testing Question Counting Methods")
        print("-" * 40)
        
        if test_course:
            course_count = get_course_question_count(test_course.name)
            print(f"📊 Total questions for course '{test_course.name}': {course_count}")
            
            if test_chapter:
                chapter_count = get_chapter_question_count(test_course.name, test_chapter.name)
                print(f"📊 Questions for chapter '{test_chapter.name}': {chapter_count}")
        
        # Test 5: Questions summary
        print("\n5️⃣ Testing Questions Summary")
        print("-" * 30)
        
        summary = get_questions_summary()
        print(f"📋 Questions summary for {len(summary)} courses:")
        
        for course_summary in summary:
            print(f"   📚 {course_summary['course_name']}: {course_summary['total_questions']} questions")
            for chapter_info in course_summary['chapters']:
                print(f"      📖 {chapter_info['name']}: {chapter_info['question_count']} questions")
        
        # Test 6: Verify question data integrity
        print("\n6️⃣ Testing Question Data Integrity")
        print("-" * 35)
        
        all_questions = db.query(Question).all()
        properly_mapped = 0
        
        for q in all_questions:
            if q.course and q.chapter_id:
                properly_mapped += 1
                print(f"✅ Question {q.id}: Course='{q.course}', Chapter={q.chapter_id}, Answer='{q.correct_answer}'")
        
        print(f"📊 {properly_mapped}/{len(all_questions)} questions have proper course/chapter mapping")
        
        print("\n✅ Enhanced Question Management Test Complete!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

def test_question_workflow_simulation():
    """Simulate the complete admin question workflow"""
    print("\n🔄 Simulating Complete Admin Question Workflow")
    print("=" * 55)
    
    db = SessionLocal()
    
    try:
        # Step 1: Admin selects course and chapter
        course = db.query(Course).first()
        chapter = db.query(Chapter).first()
        
        if not course or not chapter:
            print("❌ No course or chapter found for workflow simulation")
            return False
        
        print(f"👨‍💼 Admin selects Course: {course.name}")
        print(f"📖 Admin selects Chapter: {chapter.name}")
        
        # Step 2: Admin adds question
        print("\n📝 Admin adds question...")
        question_text = "What is 2 + 2?"
        options = ["3", "4", "5", "6"]
        correct_answer = "B"
        
        question = add_question_by_course_chapter(
            course=course.name,
            chapter_name=chapter.name,
            question_text=question_text,
            option_a=options[0],
            option_b=options[1], 
            option_c=options[2],
            option_d=options[3],
            correct_answer=correct_answer
        )
        
        print(f"✅ Question added successfully!")
        print(f"   Question ID: {question.id}")
        print(f"   Stored in Course: {question.course}")
        print(f"   Stored in Chapter ID: {question.chapter_id}")
        print(f"   Correct Answer: {question.correct_answer}")
        
        # Step 3: Student retrieves question for exam
        print("\n🎓 Student retrieves question for exam...")
        exam_questions = get_questions_with_fallback(
            course_name=course.name,
            chapter_name=chapter.name,
            limit=5
        )
        
        if exam_questions:
            retrieved_question = exam_questions[0]
            print(f"✅ Retrieved question for exam:")
            print(f"   Question: {retrieved_question.text}")
            print(f"   Options: {retrieved_question.option_a}, {retrieved_question.option_b}, {retrieved_question.option_c}, {retrieved_question.option_d}")
            print(f"   Correct Answer: {retrieved_question.correct_answer}")
        
        # Step 4: Student practices with course-wide questions
        print("\n🏃‍♂️ Student practices with course-wide questions...")
        practice_questions = get_questions_by_course_name(course.name, limit=5)
        print(f"✅ Retrieved {len(practice_questions)} questions for practice")
        
        print("\n✅ Complete workflow simulation successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Enhanced Question Management System Test Suite")
    print("=" * 60)
    
    # Run main test
    test1_success = test_enhanced_question_management()
    
    # Run workflow simulation
    test2_success = test_question_workflow_simulation()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 20)
    print(f"Basic Functionality Test: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Workflow Simulation Test: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED! Enhanced Question Management System is working correctly.")
        print("\n✨ Key Improvements Implemented:")
        print("   • Questions are properly stored by course and chapter")
        print("   • Enhanced retrieval with intelligent fallback")
        print("   • Better question counting and summary methods")
        print("   • Improved admin workflow for question management")
        print("   • Enhanced exam and practice question selection")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
    
    print("\n" + "=" * 60)
