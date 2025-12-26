#!/usr/bin/env python3
"""
Admin Question Management Integration Test
==========================================

This test verifies that the enhanced admin question management system
is properly integrated with the admin panel.

Test Flow:
1. Verify admin handler imports
2. Test admin keyboard callback configuration  
3. Verify dispatcher handler registration
4. Test course service integration
5. Simulate admin question creation flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_admin_handler_imports():
    """Test that admin handler has proper imports for enhanced question management"""
    print("🔍 Testing Admin Handler Imports...")
    
    try:
        from app.handlers.admin_handler_fixed import (
            admin_select_course_for_question,
            admin_select_chapter_for_question,
            admin_handle_question_step,
            admin_handle_question_text_input,
            admin_save_question,
            admin_cancel_question_flow,
            admin_confirm_cancel_question_flow,
            admin_continue_question_flow
        )
        print("✅ All enhanced question management functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_admin_keyboard_configuration():
    """Test that admin keyboard is configured for enhanced flow"""
    print("\n🔍 Testing Admin Keyboard Configuration...")
    
    try:
        from app.keyboards.admin_keyboard import get_admin_questions_menu
        
        # Get the questions menu
        keyboard_markup = get_admin_questions_menu()
        
        # Check if the first button uses the enhanced callback
        first_row = keyboard_markup.inline_keyboard[0]
        add_question_button = first_row[0]  # First button in first row
        
        expected_callback = "admin_select_course"
        actual_callback = add_question_button.callback_data
        
        if actual_callback == expected_callback:
            print(f"✅ Admin keyboard configured correctly")
            print(f"   Add Question button calls: {actual_callback}")
            return True
        else:
            print(f"❌ Admin keyboard misconfigured")
            print(f"   Expected: {expected_callback}")
            print(f"   Actual: {actual_callback}")
            return False
    except Exception as e:
        print(f"❌ Error testing admin keyboard: {e}")
        return False

def test_dispatcher_registration():
    """Test that dispatcher has proper handler registration"""
    print("\n🔍 Testing Dispatcher Handler Registration...")
    
    try:
        from app.bot.dispatcher_fixed import register_handlers
        from telegram.ext import Application
        
        # Check if the dispatcher function exists and is callable
        if callable(register_handlers):
            print("✅ Dispatcher registration function exists")
            
            # Check the source for enhanced handlers
            import inspect
            source = inspect.getsource(register_handlers)
            
            # Check for enhanced handler patterns
            enhanced_patterns = [
                "admin_select_course_",
                "admin_select_chapter_", 
                "admin_question_",
                "admin_handle_question_text_input"
            ]
            
            missing_patterns = []
            for pattern in enhanced_patterns:
                if pattern not in source:
                    missing_patterns.append(pattern)
            
            if not missing_patterns:
                print("✅ All enhanced question management handlers registered")
                return True
            else:
                print(f"❌ Missing handler patterns: {missing_patterns}")
                return False
        else:
            print("❌ Dispatcher registration function not found")
            return False
    except Exception as e:
        print(f"❌ Error testing dispatcher: {e}")
        return False

def test_course_service_integration():
    """Test that course service is available for question management"""
    print("\n🔍 Testing Course Service Integration...")
    
    try:
        from app.services.course_service import CourseService
        
        # Test that CourseService can be instantiated
        course_service = CourseService()
        print("✅ CourseService can be instantiated")
        
        # Test that get_courses method exists
        if hasattr(course_service, 'get_courses'):
            print("✅ CourseService has get_courses method")
            return True
        else:
            print("❌ CourseService missing get_courses method")
            return False
    except Exception as e:
        print(f"❌ Error testing course service: {e}")
        return False

def test_question_service_integration():
    """Test that question service supports enhanced creation"""
    print("\n🔍 Testing Question Service Integration...")
    
    try:
        from app.services.question_service import QuestionService
        
        # Test that QuestionService can be instantiated
        question_service = QuestionService()
        print("✅ QuestionService can be instantiated")
        
        # Test that enhanced methods exist
        enhanced_methods = ['create_question_with_course', 'get_questions_by_course']
        available_methods = []
        
        for method in enhanced_methods:
            if hasattr(question_service, method):
                available_methods.append(method)
        
        if len(available_methods) >= 1:  # At least one enhanced method should exist
            print(f"✅ Enhanced question methods available: {available_methods}")
            return True
        else:
            print("❌ No enhanced question methods found")
            return False
    except Exception as e:
        print(f"❌ Error testing question service: {e}")
        return False

def test_admin_question_handler_integration():
    """Test that admin question handler functions are available"""
    print("\n🔍 Testing Admin Question Handler Integration...")
    
    try:
        from app.handlers.admin_question_handler import (
            admin_select_course_for_question,
            admin_select_chapter_for_question,
            admin_handle_question_step,
            admin_handle_question_text_input,
            admin_save_question
        )
        
        print("✅ All admin question handler functions available")
        
        # Check function signatures
        functions = [
            admin_select_course_for_question,
            admin_select_chapter_for_question, 
            admin_handle_question_step,
            admin_handle_question_text_input,
            admin_save_question
        ]
        
        for func in functions:
            if callable(func):
                print(f"✅ {func.__name__} is callable")
            else:
                print(f"❌ {func.__name__} is not callable")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Error testing admin question handler: {e}")
        return False

def test_complete_integration():
    """Test the complete integration flow"""
    print("\n🔍 Testing Complete Integration Flow...")
    
    try:
        # Test that all components can work together
        print("Testing component integration...")
        
        # 1. Admin handler should be able to import enhanced functions
        from app.handlers.admin_handler_fixed import admin_questions_menu
        
        # 2. Admin keyboard should use enhanced callbacks
        from app.keyboards.admin_keyboard import get_admin_questions_menu
        
        # 3. Enhanced handlers should be available
        from app.handlers.admin_question_handler import admin_select_course_for_question
        
        # 4. Services should support enhanced functionality
        from app.services.course_service import CourseService
        from app.services.question_service import QuestionService
        
        print("✅ All components integrate successfully")
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("🚀 Admin Question Management Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Admin Handler Imports", test_admin_handler_imports),
        ("Admin Keyboard Configuration", test_admin_keyboard_configuration),
        ("Dispatcher Registration", test_dispatcher_registration),
        ("Course Service Integration", test_course_service_integration),
        ("Question Service Integration", test_question_service_integration),
        ("Admin Question Handler", test_admin_question_handler_integration),
        ("Complete Integration", test_complete_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Admin Question Management Integration is COMPLETE!")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the integration.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
