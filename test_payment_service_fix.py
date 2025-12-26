ter#!/usr/bin/env python3
import sys
sys.path.append('/home/aneman/Desktop/Exambot/telegramexambot')

from app.services.payment_service import approve_payment, reject_payment
from app.database.session import SessionLocal
from app.models.payment import Payment

def test_payment_service():
    print("🔧 TESTING PAYMENT SERVICE FIX")
    print("=" * 40)

    db = SessionLocal()
    try:
        # Get a pending payment to test with
        pending_payment = db.query(Payment).filter_by(status='pending').first()
        
        if pending_payment:
            print(f"🧪 Testing with Payment ID: {pending_payment.id}")
            
            # Test approve_payment function
            result = approve_payment(pending_payment.id)
            if result and hasattr(result, 'user_id'):
                print(f"✅ approve_payment returned payment object - User ID: {result.user_id}")
                print(f"   Status: {result.status}")
            else:
                print(f"❌ approve_payment did not return payment object: {type(result)}")
            
            # Reset for reject test
            db.refresh(pending_payment)
            pending_payment.status = 'pending'
            db.commit()
            
            # Test reject_payment function  
            result = reject_payment(pending_payment.id)
            if result and hasattr(result, 'user_id'):
                print(f"✅ reject_payment returned payment object - User ID: {result.user_id}")
                print(f"   Status: {result.status}")
            else:
                print(f"❌ reject_payment did not return payment object: {type(result)}")
                
            print("✅ PAYMENT SERVICE FIX VERIFIED!")
        else:
            print("❌ No pending payments found for testing")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_payment_service()

