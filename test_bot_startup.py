#!/usr/bin/env python3
"""
Comprehensive bot startup test to identify issues
"""

import sys
import traceback
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        from app.config.settings import BOT_TOKEN, DATABASE_URL
        print(f"✅ Settings loaded - Token: {BOT_TOKEN[:20]}...")
    except Exception as e:
        print(f"❌ Settings import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from app.database.base import Base
        from app.database.session import engine
        print("✅ Database imports successful")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from app.models.user import User
        from app.models.payment import Payment
        from app.models.course import Course
        from app.models.question import Question
        from app.models.exam import Exam
        from app.models.answer import Answer
        from app.models.result import Result
        print("✅ Models import successful")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from app.bot.dispatcher_fixed import register_handlers
        print("✅ Dispatcher imports successful")
    except Exception as e:
        print(f"❌ Dispatcher import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from telegram.ext import ApplicationBuilder
        print("✅ Telegram imports successful")
    except Exception as e:
        print(f"❌ Telegram import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_database_connection():
    """Test database connection and table creation"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from app.database.base import Base
        from app.database.session import engine
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test session
        from app.database.session import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection test successful")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        traceback.print_exc()
        return False

def test_handler_imports():
    """Test handler imports"""
    print("\n👥 Testing handler imports...")
    
    handlers = [
        'app.handlers.start_handler',
        'app.handlers.register_handler',
        'app.handlers.menu_handler',
        'app.handlers.profile_handler_fixed',
        'app.handlers.community_handler',
        'app.handlers.materials_handler',
        'app.handlers.help_handler',
        'app.handlers.payment_handler',
        'app.handlers.admin_handler',
        'app.handlers.course_handler',
        'app.handlers.question_handler',
        'app.handlers.stream_dashboard_handler',
        'app.handlers.stream_course_handler',
        'app.handlers.practice_handler',
        'app.handlers.radio_question_handler'
    ]
    
    failed_imports = []
    
    for handler in handlers:
        try:
            __import__(handler)
            print(f"✅ {handler}")
        except Exception as e:
            print(f"❌ {handler}: {e}")
            failed_imports.append((handler, str(e)))
    
    if failed_imports:
        print(f"\n❌ Found {len(failed_imports)} handler import issues")
        for handler, error in failed_imports:
            print(f"{handler}: {error}")
        return False
    else:
        print("\n✅ All handlers import successfully!")
        return True

def test_keyboard_imports():
    """Test keyboard imports"""
    print("\n⌨️ Testing keyboard imports...")
    
    keyboards = [
        'app.keyboards.main_menu',
        'app.keyboards.admin_keyboard',
        'app.keyboards.payment_keyboard',
        'app.keyboards.course_keyboard',
        'app.keyboards.exam_keyboard',
        'app.keyboards.level_keyboard',
        'app.keyboards.stream_keyboard',
        'app.keyboards.stream_course_keyboard'
    ]
    
    failed_imports = []
    
    for keyboard in keyboards:
        try:
            __import__(keyboard)
            print(f"✅ {keyboard}")
        except Exception as e:
            print(f"❌ {keyboard}: {e}")
            failed_imports.append((keyboard, str(e)))
    
    if failed_imports:
        print(f"\n❌ Found {len(failed_imports)} keyboard import issues")
        for keyboard, error in failed_imports:
            print(f"{keyboard}: {error}")
        return False
    else:
        print("\n✅ All keyboards import successfully!")
        return True

def test_bot_creation():
    """Test basic bot application creation"""
    print("\n🤖 Testing bot application creation...")
    
    try:
        from telegram.ext import ApplicationBuilder
        from app.config.settings import BOT_TOKEN
        
        # Build application
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        print("✅ Bot application created successfully")
        
        # Test handler registration
        from app.bot.dispatcher_fixed import register_handlers
        register_handlers(app)
        print("✅ Handlers registered successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting comprehensive bot startup test...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database_connection),
        ("Handler Import Test", test_handler_imports),
        ("Keyboard Import Test", test_keyboard_imports),
        ("Bot Creation Test", test_bot_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
            traceback.print_exc()
    
    print(f"\n{'='*50}")
    print(f"FINAL RESULTS: {passed}/{total} tests passed")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 All tests passed! Bot should be ready to run.")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed. Fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
