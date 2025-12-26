#!/usr/bin/env python3
"""
Test script to verify admin approve/reject button functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.payment import Payment
from app.models.user import User
from app.services.payment_service import approve_payment, reject_payment

def test_payment_approval_functionality():
    """Test payment approval and rejection functionality"""
    print("=== TESTING PAYMENT APPROVAL FUNCTIONALITY ===")

    db = SessionLocal()

    try:
        # Test 1: Check if there are any pending payments
        payments = db.query(Payment).filter_by(status="PENDING").all()
        print(f"1. Found {len(payments)} pending payments:")
        for payment in payments:
            user = db.query(User).filter_by(id=payment.user_id).first()
            username = f"@{user.username}" if user and user.username else f"ID: {user.telegram_id}" if user else "Unknown User"
            print(f"   Payment ID: {payment.id}, User: {username}, Status: {payment.status}")
            print(f"   Proof: {payment.proof[:50]}...")
            print()

        # Test 2: Test approve_payment function
        if payments:
            test_payment = payments[0]
            print(f"2. Testing approve_payment function for payment ID {test_payment.id}")
            
            # Get user info before approval
            user_before = db.query(User).filter_by(id=test_payment.user_id).first()
            print(f"   User access before approval: {user_before.access if user_before else 'User not found'}")
            
            # Test approval
            success = approve_payment(test_payment.id)
            if success:
                print("   ✅ approve_payment returned True")
                
                # Check user status after approval
                user_after = db.query(User).filter_by(id=test_payment.user_id).first()
                print(f"   User access after approval: {user_after.access if user_after else 'User not found'}")
                
                # Check payment status
                payment_after = db.query(Payment).filter_by(id=test_payment.id).first()
                print(f"   Payment status after approval: {payment_after.status if payment_after else 'Payment not found'}")
            else:
                print("   ❌ approve_payment returned False")

        # Test 3: Test reject_payment function
        payments_after_approval = db.query(Payment).filter_by(status="PENDING").all()
        if payments_after_approval:
            test_payment = payments_after_approval[0]
            print(f"3. Testing reject_payment function for payment ID {test_payment.id}")
            
            # Get user info before rejection
            user_before = db.query(User).filter_by(id=test_payment.user_id).first()
            print(f"   User access before rejection: {user_before.access if user_before else 'User not found'}")
            
            # Test rejection
            success = reject_payment(test_payment.id)
            if success:
                print("   ✅ reject_payment returned True")
                
                # Check user status after rejection
                user_after = db.query(User).filter_by(id=test_payment.user_id).first()
                print(f"   User access after rejection: {user_after.access if user_after else 'User not found'}")
                
                # Check payment status
                payment_after = db.query(Payment).filter_by(id=test_payment.id).first()
                print(f"   Payment status after rejection: {payment_after.status if payment_after else 'Payment not found'}")
            else:
                print("   ❌ reject_payment returned False")
        else:
            print("3. No pending payments available for rejection test")

        # Test 4: Simulate callback data patterns
        print("4. Testing callback data patterns:")
        if payments:
            payment = payments[0]
            
            # Simulate the callback data that would be created
            approve_callback = f"approve_payment_{payment.id}"
            reject_callback = f"reject_payment_{payment.id}"
            
            print(f"   Approve callback: {approve_callback}")
            print(f"   Reject callback: {reject_callback}")
            
            # Extract IDs from callback data
            extracted_approve_id = int(approve_callback.split("_")[-1])
            extracted_reject_id = int(reject_callback.split("_")[-1])
            
            print(f"   Extracted approve ID: {extracted_approve_id}")
            print(f"   Extracted reject ID: {extracted_reject_id}")
            
            if extracted_approve_id == payment.id and extracted_reject_id == payment.id:
                print("   ✅ Callback data extraction works correctly")
            else:
                print("   ❌ Callback data extraction failed")

        print("\n=== TEST COMPLETED ===")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_payment_approval_functionality()
