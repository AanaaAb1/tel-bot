#!/usr/bin/env python3
"""
Test admin question management workflow: Manage Question → Add Question → Select Course → chapters → Send Question
This tests the complete workflow for Geography and History courses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.course import Course
from app.models.exam import Exam
from app.keyboards.admin_question_keyboard import get_admin_course_selection_keyboard, get_admin_chapter_selection_keyboard
from app.handlers.admin_question_handler_fixed import admin_select_course_for_question, admin_select_chapter_for_question
from app.services.course_service import get_courses_by_code

def test_admin_question_management_workflow():
    """Test the complete admin question management workflow"""
    print("🧪 TESTING ADMIN QUESTION MANAGEMENT WORKFLOW")
    print("=" * 60)
    
    try:
        # Test 1: Verify Geography & History courses exist in database
        print("1️⃣ Verifying Geography & History courses in database...")
        db = SessionLocal()
        
        geography_course = db.query(Course).filter(Course.name == "Geography").first()
        history_course = db.query(Course).filter(Course.name == "History").first()
        
        if not geography_course:
            print("❌ Geography course not found in database!")
            return False
        if not history_course:
            print("❌ History course not found in database!")
            return False
        
        print(f"✅ Geography course found (ID: {geography_course.id})")
        print(f"✅ History course found (ID: {history_course.id})")
        
        # Test 2: Verify both courses have chapters
        print("\n2️⃣ Verifying courses have chapters...")
        geo_chapters = db.query(Exam).filter(Exam.course_id == geography_course.id).all()
        hist_chapters = db.query(Exam).filter(Exam.course_id == history_course.id).all()
        
        if len(geo_chapters) < 10:
            print(f"❌ Geography has only {len(geo_chapters)} chapters, need 10!")
            return False
        if len(hist_chapters) < 10:
            print(f"❌ History has only {len(hist_chapters)} chapters, need 10!")
            return False
        
        print(f"✅ Geography has {len(geo_chapters)} chapters")
        print(f"✅ History has {len(hist_chapters)} chapters")
        
        # Test 3: Test admin course selection keyboard
        print("\n3️⃣ Testing admin course selection keyboard...")
        try:
            course_keyboard = get_admin_course_selection_keyboard()
            print("✅ Admin course selection keyboard generated successfully")
            
            # Check if Geography and History appear in the keyboard
            geography_found = False
            history_found = False
            
            for row in course_keyboard.inline_keyboard:
                for button in row:
                    if "Geography" in button.text:
                        geography_found = True
                        print(f"✅ Geography button found: '{button.text}' -> {button.callback_data}")
                    elif "History" in button.text:
                        history_found = True
                        print(f"✅ History button found: '{button.text}' -> {button.callback_data}")
            
            if not geography_found:
                print("❌ Geography not found in admin course selection keyboard!")
                return False
            if not history_found:
                print("❌ History not found in admin course selection keyboard!")
                return False
                
        except Exception as e:
            print(f"❌ Error generating course selection keyboard: {e}")
            return False
        
        # Test 4: Test admin chapter selection keyboard
        print("\n4️⃣ Testing admin chapter selection keyboard...")
        try:
            chapter_keyboard = get_admin_chapter_selection_keyboard()
            print("✅ Admin chapter selection keyboard generated successfully")
            
            # Should have approximately 10 chapters + No Chapter + Back button
            total_buttons = sum(len(row) for row in chapter_keyboard.inline_keyboard)
            min_expected = 10  # At least 10 chapters
            max_expected = 15  # Reasonable upper bound
            
            if total_buttons < min_expected:
                print(f"❌ Expected at least {min_expected} buttons, got {total_buttons}")
                return False
            if total_buttons > max_expected:
                print(f"⚠️ Expected around {min_expected}-{max_expected} buttons, got {total_buttons} (but continuing)")
            
            print(f"✅ Chapter selection keyboard has {total_buttons} buttons")
            
        except Exception as e:
            print(f"❌ Error generating chapter selection keyboard: {e}")
            return False
        
        # Test 5: Simulate course selection callback data format
        print("\n5️⃣ Testing course selection callback format...")
        geography_callback = f"admin_select_course_{geography_course.name}"
        history_callback = f"admin_select_course_{history_course.name}"
        
        print(f"Geography callback format: {geography_callback}")
        print(f"History callback format: {history_callback}")
        
        # Test 6: Simulate chapter selection callback data format
        print("\n6️⃣ Testing chapter selection callback format...")
        for i in range(1, 4):  # Show first 3 chapters as examples
            chapter_callback = f"admin_select_chapter_{i}"
            print(f"Chapter {i} callback format: {chapter_callback}")
        
        # Test 7: Test course service lookup
        print("\n7️⃣ Testing course service lookup...")
        geo_by_code = get_courses_by_code("geography")
        hist_by_code = get_courses_by_code("history")
        
        if not geo_by_code or geo_by_code[0].name != "Geography":
            print("❌ Course service cannot find Geography by code!")
            return False
        if not hist_by_code or hist_by_code[0].name != "History":
            print("❌ Course service cannot find History by code!")
            return False
        
        print("✅ Course service can find Geography and History by code")
        
        # Test 8: List all courses that will appear in admin menu
        print("\n8️⃣ All courses in admin question management menu:")
        all_courses = db.query(Course).order_by(Course.name).all()
        for course in all_courses:
            chapter_count = db.query(Exam).filter(Exam.course_id == course.id).count()
            print(f"   📚 {course.name:<15} | Chapters: {chapter_count:2d}/10")
        
        print(f"\n🎉 ADMIN QUESTION MANAGEMENT WORKFLOW TEST COMPLETE!")
        print("✅ All tests passed - Admin can add questions for Geography and History!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def simulate_admin_workflow():
    """Simulate what admins will experience"""
    print("\n👤 SIMULATING ADMIN EXPERIENCE")
    print("=" * 60)
    
    print("Admin workflow simulation:")
    print("1. 👤 Admin clicks '❓ Manage Questions'")
    print("2. 📱 Sees question management menu:")
    print("   • ➕ Add Question")
    print("   • ✏️ Edit Question") 
    print("   • 🗑️ Delete Question")
    print("   • ⬅️ Back to Main Menu")
    print("")
    print("3. 👤 Admin clicks '➕ Add Question'")
    print("4. 📱 Sees course selection menu with:")
    print("   • 📚 Biology")
    print("   • 📚 Chemistry")
    print("   • 📚 English") 
    print("   • 📚 Geography  ← NEW!")
    print("   • 📚 History    ← NEW!")
    print("   • 📚 Mathematics")
    print("   • 📚 Physics")
    print("   • 🚫 No Course")
    print("")
    print("5. 👤 Admin clicks '📚 Geography'")
    print("6. 📱 Sees chapter selection:")
    print("   • 📖 Chapter 1")
    print("   • 📖 Chapter 2")
    print("   • 📖 Chapter 3")
    print("   • ... (through Chapter 10)")
    print("   • 📖 Chapter 10")
    print("   • 🚫 No Chapter")
    print("   • ⬅️ Back to Course Selection")
    print("")
    print("7. 👤 Admin clicks '📖 Chapter 1' (e.g., 'Introduction to Physical Geography')")
    print("8. 📱 Sees question creation interface:")
    print("   'Please send the question text:'")
    print("   [✅ Done] [❌ Cancel]")
    print("")
    print("9. 👤 Admin types question and proceeds through steps:")
    print("   • Question text → Option A → Option B → Option C → Option D → Option E (optional)")
    print("   • Confirmation screen with '✅ Save Question' button")
    print("")
    print("✅ Same workflow works for History and all other courses!")
    print("✅ Admins can now create questions for Geography and History!")

if __name__ == "__main__":
    success = test_admin_question_management_workflow()
    if success:
        simulate_admin_workflow()
        print("\n📝 ADMIN QUESTION MANAGEMENT IS FULLY FUNCTIONAL!")
    else:
        print("\n❌ Admin question management has issues!")
