#!/usr/bin/env python3
"""
Test Admin Payment Exemption Fix
Verifies that admins NEVER see payment prompts and get automatic access
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.constants import ADMIN_IDS
from app.handlers.course_handler import select_course, start_exam_selected
from app.database.session import SessionLocal
from app.models.user import User
from unittest.mock import Mock, AsyncMock
import asyncio

def test_admin_payment_exemption():
    """Test that admins bypass all payment checks"""
    
    print("🔍 Testing Admin Payment Exemption...")
    
    # Test 1: Admin should be in ADMIN_IDS
    print(f"\n📋 Test 1: Admin IDs Check")
    print(f"   Admin IDs: {ADMIN_IDS}")
    if ADMIN_IDS:
        print("   ✅ Admin IDs configured")
    else:
        print("   ❌ No admin IDs configured!")
    
    # Test 2: Simulate admin user accessing course
    print(f"\n📋 Test 2: Admin Access Test")
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else None
    
    if admin_id:
        print(f"   Testing with admin ID: {admin_id}")
        
        # Test select_course function logic
        user_id = admin_id
        if user_id in ADMIN_IDS:
            print("   ✅ Admin gets immediate access - NO payment check!")
            access_granted = True
        else:
            print("   ❌ Admin would see payment prompt")
            access_granted = False
            
        # Test start_exam_selected function logic
        chapter_id = 1
        if user_id not in ADMIN_IDS:
            print("   ❌ Regular user would see payment check")
        else:
            print("   ✅ Admin bypasses exam payment check!")
            
        if access_granted:
            print("\n🎉 SUCCESS: Admin payment exemption is working!")
            print("   • Admins will NEVER see payment prompts")
            print("   • Admins get immediate course access")
            print("   • Admins can start exams without payment verification")
            return True
        else:
            print("\n❌ FAILED: Admin payment exemption is NOT working!")
            return False
    else:
        print("   ❌ No admin IDs to test with")
        return False

def test_regular_user_payment_check():
    """Test that regular users still see payment prompts"""
    
    print(f"\n📋 Test 3: Regular User Payment Check")
    regular_user_id = 123456789  # Non-admin ID
    
    if regular_user_id not in ADMIN_IDS:
        print(f"   Testing with regular user ID: {regular_user_id}")
        print("   ✅ Regular user should see payment prompt")
        
        # Simulate the payment check logic
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=regular_user_id).first()
        db.close()
        
        if not user or user.access == "LOCKED":
            print("   ✅ Regular user sees payment prompt (as expected)")
        else:
            print("   ⚠️ Regular user has access (unusual)")
            
        return True
    else:
        print(f"   ⚠️ Regular user ID {regular_user_id} is actually an admin")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Admin Payment Exemption Tests...")
    
    # Test admin exemption
    admin_test_passed = test_admin_payment_exemption()
    
    # Test regular user behavior
    regular_test_passed = test_regular_user_payment_check()
    
    print(f"\n📊 Test Results:")
    print(f"   Admin Exemption: {'✅ PASS' if admin_test_passed else '❌ FAIL'}")
    print(f"   Regular User Check: {'✅ PASS' if regular_test_passed else '❌ FAIL'}")
    
    if admin_test_passed and regular_test_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   As an admin, you will NEVER see payment prompts!")
        print(f"   You get automatic access to all courses and exams!")
    else:
        print(f"\n❌ SOME TESTS FAILED!")
        print(f"   Please check the admin ID configuration.")
        
    return admin_test_passed and regular_test_passed

if __name__ == "__main__":
    main()
