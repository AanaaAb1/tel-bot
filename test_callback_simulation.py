ter name="content">
#!/usr/bin/env python3
"""
Test to simulate approve/reject button callback functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock telegram update and context objects
class MockUpdate:
    def __init__(self, callback_data):
        self.callback_query = MockCallbackQuery(callback_data)
        self.effective_user = MockUser(5642507992)  # Admin ID

class MockCallbackQuery:
    def __init__(self, data):
        self.data = data
        self.message = MockMessage()

    async def answer(self, text=None):
        print(f"Callback answered: {text}")

class MockMessage:
    async def edit_text(self, text, reply_markup=None):
        print(f"Message edited: {text[:100]}...")
        if reply_markup:
            print(f"Reply markup: {reply_markup.inline_keyboard}")

class MockUser:
    def __init__(self, user_id):
        self.id = user_id

class MockContext:
    def __init__(self):
        self.bot = MockBot()
        self.user_data = {}

class MockBot:
    async def send_message(self, chat_id, text, reply_markup=None):
        print(f"Bot sending message to {chat_id}: {text[:100]}...")

async def test_approve_reject_callbacks():
    """Test the approve/reject callback functionality"""
    print("=== TESTING APPROVE/REJECT CALLBACKS ===")

    # Import the handlers
    try:
        from app.handlers.admin_handler import admin_approve_payment, admin_reject_payment
        print("✅ Successfully imported admin handlers")
    except Exception as e:
        print(f"❌ Failed to import admin handlers: {e}")
        return

    # Test approve callback
    print("\n🟢 Testing approve payment callback:")
    approve_update = MockUpdate("approve_payment_1")
    context = MockContext()
    
    try:
        await admin_approve_payment(approve_update, context)
        print("✅ Approve callback executed successfully")
    except Exception as e:
        print(f"❌ Approve callback failed: {e}")
        import traceback
        traceback.print_exc()

    # Test reject callback  
    print("\n🔴 Testing reject payment callback:")
    reject_update = MockUpdate("reject_payment_2")
    context = MockContext()
    
    try:
        await admin_reject_payment(reject_update, context)
        print("✅ Reject callback executed successfully")
    except Exception as e:
        print(f"❌ Reject callback failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_approve_reject_callbacks())
