#!/usr/bin/env python3
"""
Comprehensive import test to identify all conflicts
"""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

def test_all_imports():
    """Test all relevant imports step by step"""
    print("=" * 60)
    print("COMPREHENSIVE IMPORT TEST")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Import admin_question_handler_fixed
    total_tests += 1
    print(f"\n🔍 Test {total_tests}: Import admin_question_handler_fixed")
    try:
        from app.handlers.admin_question_handler_fixed import admin_select_course_for_question
        print("✅ SUCCESS: admin_question_handler_fixed imported successfully!")
        success_count += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 2: Import admin_handler_fixed
    total_tests += 1
    print(f"\n🔍 Test {total_tests}: Import admin_handler_fixed")
    try:
        from app.handlers.admin_handler_fixed import admin_panel
        print("✅ SUCCESS: admin_handler_fixed imported successfully!")
        success_count += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 3: Check if broken admin_question_handler still exists
    total_tests += 1
    print(f"\n🔍 Test {total_tests}: Check broken admin_question_handler exists")
    try:
        broken_handler_path = Path(__file__).parent / "app" / "handlers" / "admin_question_handler.py"
        if broken_handler_path.exists():
            print(f"⚠️  WARNING: Broken handler still exists at {broken_handler_path}")
            print("🔧 RECOMMENDATION: Remove this file to prevent conflicts")
        else:
            print("✅ SUCCESS: Broken handler file does not exist")
            success_count += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 4: Import dispatcher_fixed
    total_tests += 1
    print(f"\n🔍 Test {total_tests}: Import dispatcher_fixed")
    try:
        from app.bot.dispatcher_fixed import register_handlers
        print("✅ SUCCESS: dispatcher_fixed imported successfully!")
        success_count += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 5: Check imports from dispatcher
    total_tests += 1
    print(f"\n🔍 Test {total_tests}: Check all imports from dispatcher_fixed")
    try:
        from app.bot.dispatcher_fixed import (
            admin_payments, approve, reject, exam_analytics,
            admin_panel, admin_users, 
            admin_results, admin_export_menu, admin_export_csv, admin_export_excel,
            admin_back_main, handle_admin_text_input, edit_question, delete_question, admin_confirm_delete,
            admin_view_payment_details, admin_approve_payment, admin_reject_payment
        )
        print("✅ SUCCESS: All dispatcher imports work correctly!")
        success_count += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {success_count}/{total_tests} tests passed")
    print("=" * 60)
    
    if success_count == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Import conflicts have been resolved!")
        return True
    else:
        print(f"\n❌ {total_tests - success_count} tests failed")
        print("🔧 Import conflicts still exist!")
        return False

if __name__ == "__main__":
    success = test_all_imports()
    sys.exit(0 if success else 1)
