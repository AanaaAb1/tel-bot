#!/usr/bin/env python3
"""
Create test payment data and test approve/reject button functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.payment import Payment
from app.models.user import User
from app.services.payment_service import approve_payment, reject_payment
from datetime import datetime

def create_test_payment():
    """Create a test payment for approval testing"""
    print("=== CREATING TEST PAYMENT ===")

    db = SessionLocal()

    try:
        # Check if there are any users
        users = db.query(User).all()
        if not users:
            print("No users found in database. Cannot create test payment.")
            return None

        test_user = users[0]  # Use first user
        
        # Create test payment
        test_payment = Payment(
            user_id=test_user.id,
            amount=10.00,
            status="PENDING",
            proof="Test payment proof - Photo uploaded - fake_file_id_12345",
            created_at=datetime.now()
        )
        
        db.add(test_payment)
        db.commit()
        db.refresh(test_payment)
        
        print(f"✅ Created test payment ID: {test_payment.id}")
        print(f"   User: {test_user.telegram_id} ({test_user.full_name})")
        print(f"   Status: {test_payment.status}")
        print(f"   Amount: ${test_payment.amount}")
        
        return test_payment
        
    except Exception as e:
        print(f"❌ Error creating test payment: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def test_approve_reject_buttons():
    """Test the actual approve/reject button functionality"""
    print("\n=== TESTING APPROVE/REJECT BUTTONS ===")

    # Create test payment first
    test_payment = create_test_payment()
    if not test_payment:
        return

    # Simulate the button callback data
    approve_callback = f"approve_payment_{test_payment.id}"
    reject_callback = f"reject_payment_{test_payment.id}"
    
    print(f"\nSimulating button clicks:")
    print(f"Approve button callback: {approve_callback}")
    print(f"Reject button callback: {reject_callback}")

    # Test approve functionality
    print(f"\n🟢 Testing APPROVE button:")
    try:
        success = approve_payment(test_payment.id)
        if success:
            print("   ✅ Approve function executed successfully")
            
            # Check payment status
            db = SessionLocal()
            payment_after = db.query(Payment).filter_by(id=test_payment.id).first()
            user_after = db.query(User).filter_by(id=test_payment.user_id).first()
            
            print(f"   Payment status after approve: {payment_after.status if payment_after else 'Not found'}")
            print(f"   User access after approve: {user_after.access if user_after else 'Not found'}")
            
            db.close()
        else:
            print("   ❌ Approve function failed")
    except Exception as e:
        print(f"   ❌ Error in approve function: {e}")

    # Create another test payment for rejection test
    print(f"\n🔴 Testing REJECT button:")
    test_payment2 = create_test_payment()
    if test_payment2:
        try:
            success = reject_payment(test_payment2.id)
            if success:
                print("   ✅ Reject function executed successfully")
                
                # Check payment status
                db = SessionLocal()
                payment_after = db.query(Payment).filter_by(id=test_payment2.id).first()
                user_after = db.query(User).filter_by(id=test_payment2.user_id).first()
                
                print(f"   Payment status after reject: {payment_after.status if payment_after else 'Not found'}")
                print(f"   User access after reject: {user_after.access if user_after else 'Not found'}")
                
                db.close()
            else:
                print("   ❌ Reject function failed")
        except Exception as e:
            print(f"   ❌ Error in reject function: {e}")

def test_callback_pattern_matching():
    """Test if the callback patterns match the handler patterns"""
    print("\n=== TESTING CALLBACK PATTERN MATCHING ===")

    import re

    # Handler patterns from dispatcher
    approve_pattern = r"^approve_payment_"
    reject_pattern = r"^reject_payment_"

    # Test cases
    test_callbacks = [
        "approve_payment_1",
        "approve_payment_123",
        "reject_payment_1", 
        "reject_payment_456",
        "approve_payment_abc",  # Should not match
        "reject_payment_xyz",   # Should not match
        "admin_approve_payment_1",  # Should not match
    ]

    for callback in test_callbacks:
        approve_match = re.match(approve_pattern, callback)
        reject_match = re.match(reject_pattern, callback)
        
        print(f"Callback: {callback}")
        print(f"  Matches approve pattern: {bool(approve_match)}")
        print(f"  Matches reject pattern: {bool(reject_match)}")
        
        if approve_match:
            payment_id = callback.split("_")[-1]
            print(f"  Extracted payment ID: {payment_id}")
        elif reject_match:
            payment_id = callback.split("_")[-1] 
            print(f"  Extracted payment ID: {payment_id}")
        print()

if __name__ == "__main__":
    test_approve_reject_buttons()
    test_callback_pattern_matching()
