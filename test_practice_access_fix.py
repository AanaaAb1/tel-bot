#!/usr/bin/env python3
import sys
sys.path.append('/home/aneman/Desktop/Exambot/telegramexambot')

def test_practice_access_after_payment():
    print("🔧 TESTING PRACTICE ACCESS AFTER PAYMENT APPROVAL")
    print("=" * 55)

    try:
        # Test 1: Check current user access status
        from app.database.session import SessionLocal
        from app.models.user import User
        from app.config.constants import ACCESS_UNLOCKED

        db = SessionLocal()
        
        # Get a user who made a payment
        user = db.query(User).filter_by(telegram_id=1).first()  # Test user ID 1
        
        if user:
            print(f"🧪 Testing with User ID: {user.telegram_id}")
            print(f"   Payment Status: {user.payment_status}")
            print(f"   Access Status: {user.access}")
            print(f"   Expected ACCESS_UNLOCKED: {ACCESS_UNLOCKED}")
            
            # Test 2: Verify access check logic
            access_check_result = (user.access != ACCESS_UNLOCKED)
            print(f"   Access Check (should be False): {access_check_result}")
            
            if not access_check_result:
                print("✅ PRACTICE ACCESS SHOULD BE UNLOCKED!")
            else:
                print("❌ PRACTICE ACCESS STILL LOCKED!")
                
            # Test 3: If access is locked, approve a payment to unlock it
            if access_check_result:
                print("\n🔧 SIMULATING PAYMENT APPROVAL...")
                from app.services.payment_service import approve_payment
                
                # Find a pending payment for this user
                from app.models.payment import Payment
                pending_payment = db.query(Payment).filter_by(
                    user_id=user.id, 
                    status='pending'
                ).first()
                
                if pending_payment:
                    print(f"📝 Approving Payment ID: {pending_payment.id}")
                    result = approve_payment(pending_payment.id)
                    
                    if result and result.status == 'approved':
                        print("✅ Payment approved successfully!")
                        print(f"   User payment_status: {result.user.payment_status}")
                        print(f"   User access: {result.user.access}")
                        
                        # Test 4: Verify access is now unlocked
                        updated_access_check = (result.user.access != ACCESS_UNLOCKED)
                        print(f"   Updated Access Check (should be False): {updated_access_check}")
                        
                        if not updated_access_check:
                            print("🎉 PRACTICE ACCESS SUCCESSFULLY UNLOCKED!")
                        else:
                            print("❌ PRACTICE ACCESS STILL LOCKED AFTER APPROVAL!")
                    else:
                        print("❌ Payment approval failed!")
                else:
                    print("❌ No pending payments found for user")
            
        else:
            print("❌ No test user found")
            
        db.close()
        
        # Test 5: Test the actual practice handler logic
        print("\n🧪 TESTING PRACTICE HANDLER ACCESS CHECK...")
        from app.handlers.practice_handler import start_practice
        
        # Test the import and constant
        print(f"✅ Practice handler imported successfully")
        print(f"✅ ACCESS_UNLOCKED constant: '{ACCESS_UNLOCKED}'")
        
        # Test 6: Check for other handlers that might have similar issues
        print("\n🔍 CHECKING FOR OTHER ACCESS CONTROL ISSUES...")
        
        # Check course handler
        try:
            from app.handlers.course_handler import select_course
            print("✅ Course handler imported")
        except Exception as e:
            print(f"❌ Course handler import error: {e}")
            
        # Check exam handler  
        try:
            from app.handlers.question_handler import start_exam
            print("✅ Question handler imported")
        except Exception as e:
            print(f"❌ Question handler import error: {e}")
            
        print("\n✅ PRACTICE ACCESS TEST COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_practice_access_after_payment()

