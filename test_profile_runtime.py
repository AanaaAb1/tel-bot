#!/usr/bin/env python3
"""
Test profile functionality to identify runtime issues
"""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

# Mock Telegram objects for testing
class MockUpdate:
    def __init__(self, user_id=123456789):
        self.effective_user = MockUser(user_id)
        self.callback_query = MockCallbackQuery(user_id)

class MockUser:
    def __init__(self, user_id):
        self.id = user_id
        self.first_name = "Test"
        self.last_name = "User"

class MockCallbackQuery:
    def __init__(self, user_id):
        self.data = "profile"
        self.message = MockMessage()
        self.from_user = MockUser(user_id)
        
    async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
        print(f"✅ Profile message displayed:")
        print(f"Text: {text[:200]}...")
        print(f"Reply markup: {reply_markup}")
        print("=" * 50)

class MockMessage:
    async def reply_text(self, text, reply_markup=None):
        print(f"✅ Profile message sent:")
        print(f"Text: {text[:200]}...")
        print(f"Reply markup: {reply_markup}")
        print("=" * 50)

class MockContext:
    def __init__(self):
        self.bot = MockBot()

class MockBot:
    username = "SmartTestexambot"
    
    async def send_message(self, chat_id, text):
        print(f"📤 Message sent to {chat_id}:")
        print(f"Text: {text[:200]}...")
        print("=" * 50)

# Test the profile function
async def test_profile_function():
    """Test the profile function with mock data"""
    try:
        print("🧪 Testing profile function...")
        
        # Import and test the profile function
        from app.handlers.profile_handler_fixed import profile_menu
        
        # Create mock objects
        update = MockUpdate()
        context = MockContext()
        
        print("✅ Mock objects created successfully")
        print("🚀 Calling profile_menu...")
        
        # Call the profile function
        await profile_menu(update, context)
        
        print("✅ Profile function completed successfully")
        
    except Exception as e:
        print(f"❌ Error in profile function: {e}")
        import traceback
        traceback.print_exc()

def test_database_connection():
    """Test database connection and user creation"""
    try:
        print("🗄️ Testing database connection...")
        
        from app.database.session import SessionLocal
        from app.models.user import User
        
        db = SessionLocal()
        
        # Create test user
        test_user = db.query(User).filter_by(telegram_id=123456789).first()
        if not test_user:
            test_user = User(
                telegram_id=123456789,
                full_name="Test User",
                join_time=None,
                level="freshman",
                stream="natural_science",
                payment_status="approved",
                access="UNLOCKED"
            )
            db.add(test_user)
            db.commit()
            print("✅ Test user created successfully")
        else:
            print("✅ Test user exists")
        
        print(f"👤 User data: {test_user.telegram_id}, {test_user.full_name}, {test_user.stream}")
        db.close()
        print("✅ Database test completed successfully")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Starting profile functionality test...")
    print("=" * 50)
    
    # Test database first
    test_database_connection()
    print("\n" + "=" * 50)
    
    # Test profile function
    import asyncio
    asyncio.run(test_profile_function())
    
    print("\n" + "=" * 50)
    print("🏁 Profile test completed")
