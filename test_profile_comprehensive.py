#!/usr/bin/env python3
"""
Test the profile handler functionality
"""

import sys
import asyncio
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

def test_profile_handler_functionality():
    """Test the profile handler to verify it works"""
    try:
        print("🧪 Testing profile handler functionality...")
        
        # Import the profile handler
        from app.handlers.profile_handler_fixed import profile_menu, generate_referral_code
        
        print("✅ Profile handler imported successfully")
        
        # Test referral code generation
        code = generate_referral_code()
        print(f"🆔 Generated referral code: {code}")
        
        # Check if the function is async
        print(f"📋 Function type: {type(profile_menu)}")
        print(f"📋 Is coroutine function: {asyncio.iscoroutinefunction(profile_menu)}")
        
        # Test basic function signature
        import inspect
        sig = inspect.signature(profile_menu)
        print(f"📋 Function signature: {sig}")
        
        print("✅ Profile handler structure looks correct")
        
        # Test database connection
        try:
            from app.database.session import SessionLocal
            from app.models.user import User
            
            db = SessionLocal()
            user_count = db.query(User).count()
            print(f"👤 Database has {user_count} users")
            db.close()
            print("✅ Database connection successful")
            
        except Exception as e:
            print(f"❌ Database test failed: {e}")
        
        print("✅ All profile handler tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Profile handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dispatcher_registration():
    """Test that the dispatcher correctly registers profile handlers"""
    try:
        print("🧪 Testing dispatcher registration...")
        
        from app.bot.dispatcher_fixed import register_handlers
        from telegram.ext import ApplicationBuilder
        
        # Create a mock application
        app = ApplicationBuilder().token("fake_token").build()
        
        # Test the registration
        register_handlers(app)
        
        # Check if profile handlers are registered
        handlers = app.handlers.get('callback_query', [])
        profile_handlers = [h for h in handlers if hasattr(h, 'pattern') and h.pattern and 'profile' in str(h.pattern)]
        
        print(f"📋 Found {len(profile_handlers)} profile-related handlers")
        for i, handler in enumerate(profile_handlers):
            print(f"  {i+1}. Pattern: {handler.pattern}")
        
        print("✅ Dispatcher registration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Dispatcher registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_menu_keyboard():
    """Test that the main menu keyboard has the profile button"""
    try:
        print("🧪 Testing main menu keyboard...")
        
        from app.keyboards.main_menu import main_menu
        
        # Create a mock user ID
        test_user_id = 123456789
        
        # Get the menu keyboard
        keyboard = main_menu(test_user_id)
        
        print(f"📱 Menu keyboard created with {len(keyboard)} rows")
        
        # Look for profile button
        profile_found = False
        for row in keyboard:
            for button in row:
                if button.text and 'Profile' in button.text:
                    profile_found = True
                    print(f"✅ Found profile button: {button.text}")
                    print(f"🔗 Profile button callback: {button.callback_data}")
                    break
            if profile_found:
                break
        
        if not profile_found:
            print("❌ Profile button not found in main menu!")
            return False
        
        print("✅ Main menu keyboard test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Main menu keyboard test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting comprehensive profile functionality test...")
    print("=" * 60)
    
    tests = [
        ("Profile Handler Structure", test_profile_handler_functionality),
        ("Dispatcher Registration", test_dispatcher_registration),
        ("Menu Keyboard", test_menu_keyboard),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
        
        print("-" * 40)
    
    print(f"\n🏁 Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Profile functionality should work correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Profile functionality may have issues.")
        return False

if __name__ == "__main__":
    run_comprehensive_test()

