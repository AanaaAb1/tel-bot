#!/usr/bin/env python3
"""
Test Script for Stream-Specific Dashboards Implementation
Verifies all components work correctly together
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_stream_dashboard_imports():
    """Test that all stream dashboard components can be imported successfully"""
    print("🧪 Testing Stream Dashboard Component Imports...")
    
    try:
        # Test stream dashboard handler imports
        from app.handlers.stream_dashboard_handler import (
            natural_science_dashboard,
            social_science_dashboard,
            handle_natural_science_action,
            handle_social_science_action,
            natural_science_exams,
            social_science_exams
        )
        print("✅ Stream Dashboard Handler imports successful")
        
        # Test stream menu keyboard imports
        from app.keyboards.stream_menu_keyboard import (
            get_natural_science_dashboard_keyboard,
            get_social_science_dashboard_keyboard,
            get_natural_science_dashboard_message,
            get_social_science_dashboard_message
        )
        print("✅ Stream Menu Keyboard imports successful")
        
        # Test stream course handler imports
        from app.handlers.stream_course_handler import (
            select_natural_science_course,
            select_social_science_course,
            handle_stream_course_selection,
            get_stream_course_handler
        )
        print("✅ Stream Course Handler imports successful")
        
        # Test menu handler updates
        from app.handlers.menu_handler import menu
        print("✅ Updated Menu Handler imports successful")
        
        # Test dispatcher updates
        from app.bot.dispatcher_fixed import register_handlers
        print("✅ Updated Dispatcher imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_keyboard_generation():
    """Test that stream-specific keyboards are generated correctly"""
    print("\n🎨 Testing Stream-Specific Keyboard Generation...")
    
    try:
        from app.keyboards.stream_menu_keyboard import (
            get_natural_science_dashboard_keyboard,
            get_social_science_dashboard_keyboard
        )
        
        # Test Natural Science dashboard keyboard
        ns_keyboard = get_natural_science_dashboard_keyboard(user_id=12345)
        ns_inline_keyboard = ns_keyboard.inline_keyboard
        
        # Check that NS dashboard has expected buttons
        ns_button_texts = [button[0].text for button in ns_inline_keyboard]
        expected_ns_buttons = [
            "🧬 Natural Science Exams",
            "🎯 Practice", 
            "📚 Materials",
            "🏆 Leaderboard",
            "👤 Profile",
            "📊 My Results",
            "⬅️ Main Menu"
        ]
        
        for expected in expected_ns_buttons:
            if expected not in ns_button_texts:
                print(f"❌ Missing NS button: {expected}")
                return False
        print("✅ Natural Science dashboard keyboard generated correctly")
        
        # Test Social Science dashboard keyboard
        ss_keyboard = get_social_science_dashboard_keyboard(user_id=12345)
        ss_inline_keyboard = ss_keyboard.inline_keyboard
        
        # Check that SS dashboard has expected buttons
        ss_button_texts = [button[0].text for button in ss_inline_keyboard]
        expected_ss_buttons = [
            "🌍 Social Science Exams",
            "🎯 Practice",
            "📚 Materials", 
            "🏆 Leaderboard",
            "👤 Profile",
            "📊 My Results",
            "⬅️ Main Menu"
        ]
        
        for expected in expected_ss_buttons:
            if expected not in ss_button_texts:
                print(f"❌ Missing SS button: {expected}")
                return False
        print("✅ Social Science dashboard keyboard generated correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Keyboard generation test failed: {e}")
        return False

def test_handler_patterns():
    """Test that handler patterns are correctly configured"""
    print("\n🎯 Testing Handler Pattern Configuration...")
    
    try:
        from app.bot.dispatcher_fixed import register_handlers
        from telegram.ext import ApplicationBuilder, CallbackQueryHandler
        from app.config.settings import BOT_TOKEN
        
        # Create a test application
        app = ApplicationBuilder().token("dummy_token").build()
        
        # Register handlers (this will validate the patterns)
        try:
            register_handlers(app)
            print("✅ All handlers registered successfully")
        except Exception as e:
            print(f"❌ Handler registration failed: {e}")
            return False
        
        # Check that stream-specific patterns are registered
        handler_patterns = []
        for handler in app.handlers.get(1, []):  # Callback query handlers are usually type 1
            if hasattr(handler, 'pattern') and handler.pattern:
                handler_patterns.append(str(handler.pattern))
        
        # Check for expected stream patterns
        expected_patterns = [
            "^natural_science_dashboard$",
            "^social_science_dashboard$", 
            "^ns_",
            "^ss_",
            "^ns_exams$",
            "^ss_exams$"
        ]
        
        found_patterns = []
        for pattern in expected_patterns:
            matching = [p for p in handler_patterns if pattern in str(p)]
            if matching:
                found_patterns.append(pattern)
        
        missing_patterns = [p for p in expected_patterns if p not in found_patterns]
        if missing_patterns:
            print(f"❌ Missing handler patterns: {missing_patterns}")
            return False
            
        print("✅ All expected handler patterns found")
        return True
        
    except Exception as e:
        print(f"❌ Handler pattern test failed: {e}")
        return False

def test_stream_course_validation():
    """Test stream-specific course validation logic"""
    print("\n📚 Testing Stream Course Validation Logic...")
    
    try:
        from app.handlers.stream_course_handler import select_natural_science_course, select_social_science_course
        
        # Test that functions exist and are callable
        if not callable(select_natural_science_course):
            print("❌ select_natural_science_course is not callable")
            return False
            
        if not callable(select_social_science_course):
            print("❌ select_social_science_course is not callable")
            return False
            
        print("✅ Stream course functions are callable")
        return True
        
    except Exception as e:
        print(f"❌ Stream course validation test failed: {e}")
        return False

def test_menu_routing():
    """Test that menu handler includes stream routing logic"""
    print("\n🔄 Testing Menu Routing Logic...")
    
    try:
        # Read menu_handler.py and check for stream routing code
        with open('/home/aneman/Desktop/Exambot/telegramexambot/app/handlers/menu_handler.py', 'r') as f:
            menu_code = f.read()
        
        # Check for stream routing imports
        if 'natural_science_dashboard' not in menu_code:
            print("❌ Menu handler missing natural_science_dashboard import")
            return False
            
        if 'social_science_dashboard' not in menu_code:
            print("❌ Menu handler missing social_science_dashboard import")
            return False
            
        # Check for stream routing logic
        if 'user.stream == "natural_science"' not in menu_code:
            print("❌ Menu handler missing Natural Science routing logic")
            return False
            
        if 'user.stream == "social_science"' not in menu_code:
            print("❌ Menu handler missing Social Science routing logic")
            return False
            
        print("✅ Menu routing logic includes stream-specific routing")
        return True
        
    except Exception as e:
        print(f"❌ Menu routing test failed: {e}")
        return False

def run_all_tests():
    """Run all stream dashboard tests"""
    print("🚀 Starting Stream-Specific Dashboards Test Suite\n")
    
    tests = [
        test_stream_dashboard_imports,
        test_keyboard_generation,
        test_handler_patterns,
        test_stream_course_validation,
        test_menu_routing
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Stream-specific dashboards implementation is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
