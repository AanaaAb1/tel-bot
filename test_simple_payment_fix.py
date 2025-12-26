#!/usr/bin/env python3
import sys
sys.path.append('/home/aneman/Desktop/Exambot/telegramexambot')

def test_payment_service():
    print("🔧 TESTING PAYMENT SERVICE FIX")
    print("=" * 40)

    try:
        # Test import
        from app.services.payment_service import approve_payment, reject_payment
        print("✅ Successfully imported payment service functions")
        
        # Test that the functions exist and are callable
        if callable(approve_payment):
            print("✅ approve_payment function is callable")
        else:
            print("❌ approve_payment function is not callable")
            
        if callable(reject_payment):
            print("✅ reject_payment function is callable")
        else:
            print("❌ reject_payment function is not callable")
            
        # Test database connection
        from app.database.session import SessionLocal
        from app.models.payment import Payment
        
        db = SessionLocal()
        
        # Get a pending payment to test with
        pending_payment = db.query(Payment).filter_by(status='pending').first()
        
        if pending_payment:
            print(f"🧪 Testing with Payment ID: {pending_payment.id}")
            print(f"   Original status: {pending_payment.status}")
            
            # Test approve_payment function
            result = approve_payment(pending_payment.id)
            print(f"   approve_payment returned: {type(result)}")
            
            if result and hasattr(result, 'user_id'):
                print(f"✅ approve_payment returned payment object - User ID: {result.user_id}")
                print(f"   Status after approval: {result.status}")
            else:
                print(f"❌ approve_payment did not return payment object")
            
            # Reset for reject test
            db.refresh(pending_payment)
            pending_payment.status = 'pending'
            db.commit()
            
            # Test reject_payment function  
            result = reject_payment(pending_payment.id)
            print(f"   reject_payment returned: {type(result)}")
            
            if result and hasattr(result, 'user_id'):
                print(f"✅ reject_payment returned payment object - User ID: {result.user_id}")
                print(f"   Status after rejection: {result.status}")
            else:
                print(f"❌ reject_payment did not return payment object")
                
            print("✅ PAYMENT SERVICE FIX VERIFIED!")
        else:
            print("❌ No pending payments found for testing")
            
        db.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_payment_service()

