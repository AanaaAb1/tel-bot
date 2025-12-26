#!/usr/bin/env python3
"""
Simple diagnostic test for payment approval system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== DIAGNOSTIC TEST ===")
    
    # Test imports
    print("1. Testing imports...")
    from app.database.session import SessionLocal
    print("   ✅ SessionLocal imported")
    
    from app.models.user import User
    print("   ✅ User model imported")
    
    from app.models.payment import Payment
    print("   ✅ Payment model imported")
    
    from app.services.payment_service import approve_payment, reject_payment
    print("   ✅ Payment service functions imported")
    
    from app.keyboards.admin_keyboard import get_payment_approval_keyboard
    print("   ✅ Admin keyboard imported")
    
    # Test database connection
    print("\n2. Testing database connection...")
    db = SessionLocal()
    print("   ✅ Database connected")
    
    # Test user count
    user_count = db.query(User).count()
    print(f"   Users in database: {user_count}")
    
    # Test payment count
    payment_count = db.query(Payment).count()
    print(f"   Payments in database: {payment_count}")
    
    # Test payment service functions
    print("\n3. Testing payment service functions...")
    try:
        result = approve_payment(999)  # Non-existent payment
        print(f"   approve_payment(999) returned: {result}")
    except Exception as e:
        print(f"   approve_payment error: {e}")
    
    try:
        result = reject_payment(999)  # Non-existent payment
        print(f"   reject_payment(999) returned: {result}")
    except Exception as e:
        print(f"   reject_payment error: {e}")
    
    # Test keyboard creation
    print("\n4. Testing keyboard creation...")
    try:
        keyboard = get_payment_approval_keyboard(1)
        print(f"   ✅ Keyboard created with {len(keyboard.inline_keyboard)} rows")
        for i, row in enumerate(keyboard.inline_keyboard):
            print(f"   Row {i+1}: {len(row)} buttons")
            for button in row:
                print(f"     - {button.text} (callback: {button.callback_data})")
    except Exception as e:
        print(f"   ❌ Keyboard creation error: {e}")
    
    db.close()
    print("\n=== DIAGNOSTIC COMPLETE ===")
    
except Exception as e:
    print(f"❌ Error during diagnostic: {e}")
    import traceback
    traceback.print_exc()
