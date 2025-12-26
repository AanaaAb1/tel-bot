#!/usr/bin/env python3
import sys
sys.path.append('/home/aneman/Desktop/Exambot/telegramexambot')

from app.database.session import SessionLocal
from app.models.payment import Payment
from app.models.user import User

def check_database():
    print("=== PAYMENT DATABASE CHECK ===")
    
    db = SessionLocal()
    try:
        # Check all payments
        all_payments = db.query(Payment).all()
        print(f"📊 Total payments in database: {len(all_payments)}")
        
        # Check by status
        for status in ['PENDING', 'APPROVED', 'REJECTED', 'COMPLETED']:
            count = db.query(Payment).filter_by(status=status).count()
            print(f"📋 {status}: {count}")
        
        # Show details
        if all_payments:
            print("\n📝 All payments:")
            for payment in all_payments:
                user = db.query(User).filter_by(id=payment.user_id).first()
                username = user.username if user else f"UserID:{payment.user_id}"
                print(f"   ID:{payment.id} | {username} | {payment.status} | {payment.proof[:40]}...")
        else:
            print("\n❌ No payments found in database")
            
        # Test payment creation
        print("\n=== TESTING PAYMENT CREATION ===")
        test_user = db.query(User).first()
        if test_user:
            print(f"Testing with user: {test_user.username}")
            
            # Create test payment
            from app.services.payment_service import create_payment
            payment = create_payment(test_user.id, "TEST_PAYMENT_DB_CHECK")
            
            if payment:
                print(f"✅ Payment created: ID={payment.id}, Status={payment.status}")
                
                # Verify it was stored
                stored_payment = db.query(Payment).filter_by(id=payment.id).first()
                if stored_payment:
                    print(f"✅ Payment verified in database: {stored_payment.proof}")
                else:
                    print("❌ Payment not found in database!")
            else:
                print("❌ Payment creation failed")
        else:
            print("❌ No users found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_database()

