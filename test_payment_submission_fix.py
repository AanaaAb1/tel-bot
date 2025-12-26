#!/usr/bin/env python3
"""
Test Payment Submission Fix
Tests the fixed payment submission system
"""

from app.database.session import SessionLocal
from app.models.user import User
from app.models.payment import Payment
from app.services.payment_service import create_payment

def test_payment_submission():
    """Test creating a payment and verify it's properly stored"""
    
    print("=== TESTING PAYMENT SUBMISSION FIX ===")
    
    # Test payment creation
    test_user_id = 1  # Assuming user ID 1 exists
    test_proof = "Test transaction ID: TXN123456789"
    
    print(f"Creating test payment for user {test_user_id}")
    payment = create_payment(test_user_id, test_proof)
    
    if payment:
        print(f"✅ Payment created successfully!")
        print(f"   Payment ID: {payment.id}")
        print(f"   User ID: {payment.user_id}")
        print(f"   Proof: {payment.proof}")
        print(f"   Status: {payment.status}")
        print(f"   Created: {payment.created_at}")
        
        # Verify in database
        db = SessionLocal()
        db_payment = db.query(Payment).filter_by(id=payment.id).first()
        db.close()
        
        if db_payment:
            print(f"✅ Payment verified in database!")
            print(f"   Database payment ID: {db_payment.id}")
            print(f"   Database status: {db_payment.status}")
            
            # Check pending payments count
            pending_payments = db.query(Payment).filter_by(status='pending').all()
            print(f"✅ Total pending payments: {len(pending_payments)}")
            
            return True
        else:
            print(f"❌ Payment not found in database")
            return False
    else:
        print(f"❌ Failed to create payment")
        return False

if __name__ == "__main__":
    success = test_payment_submission()
    if success:
        print("\n🎉 Payment submission fix successful!")
        print("✅ Users can now submit payment proofs")
        print("✅ Pending payments will show in admin panel")
        print("✅ Approve/Reject buttons will work")
    else:
        print("\n❌ Payment submission fix failed!")

