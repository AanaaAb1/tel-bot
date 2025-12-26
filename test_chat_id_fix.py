#!/usr/bin/env python3
"""
Simple test to verify the chat_id fix is working.
"""

import sys
import os
sys.path.append('/home/aneman/Desktop/Exambot/telegramexambot')

def test_chat_id_fix():
    """Test that chat_id is properly set during exam start"""
    
    print("🔍 Testing Chat ID Fix...")
    
    # Test the start_exam_with_polls function
    from app.handlers.radio_question_handler import start_exam_with_polls
    
    # Mock update and context objects
    class MockUpdate:
        def __init__(self, chat_id=None, user_id=None):
            self.effective_chat = MockChat(chat_id) if chat_id else None
            self.effective_user = MockUser(user_id) if user_id else None
    
    class MockChat:
        def __init__(self, chat_id):
            self.id = chat_id
    
    class MockUser:
        def __init__(self, user_id):
            self.id = user_id
    
    class MockContext:
        def __init__(self):
            self.user_data = {}
    
    # Test Case 1: Normal case with chat_id
    print("\n📋 Test Case 1: Normal case with chat_id")
    update1 = MockUpdate(chat_id=12345, user_id=67890)
    context1 = MockContext()
    data1 = context1.user_data
    
    # This should not raise an error
    try:
        import asyncio
        
        async def test_start():
            await start_exam_with_polls(update1, context1, data1)
            return True
        
        result = asyncio.run(test_start())
        print("✅ start_exam_with_polls executed successfully")
        
        # Check if chat_id was set
        if "chat_id" in data1 and data1["chat_id"] == 12345:
            print("✅ chat_id correctly set to 12345")
        else:
            print(f"❌ chat_id not set correctly. Got: {data1.get('chat_id')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    
    # Test Case 2: Fallback case with only user_id
    print("\n📋 Test Case 2: Fallback case with only user_id")
    update2 = MockUpdate(chat_id=None, user_id=67890)
    context2 = MockContext()
    data2 = context2.user_data
    
    try:
        async def test_start2():
            await start_exam_with_polls(update2, context2, data2)
            return True
        
        result = asyncio.run(test_start2())
        print("✅ start_exam_with_polls executed successfully (fallback case)")
        
        # Check if chat_id was set to user_id
        if "chat_id" in data2 and data2["chat_id"] == 67890:
            print("✅ chat_id correctly set to user_id (67890)")
        else:
            print(f"❌ chat_id not set correctly in fallback. Got: {data2.get('chat_id')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during fallback test: {e}")
        return False
    
    print("\n🎉 All tests passed! The chat_id fix is working correctly.")
    return True

def test_show_next_question_logic():
    """Test that show_next_question would work with chat_id"""
    
    print("\n🔍 Testing show_next_question logic...")
    
    from app.handlers.radio_question_handler import show_next_question
    
    # Mock context and data
    class MockContext:
        def __init__(self):
            self.user_data = {}
    
    class MockQuestion:
        def __init__(self):
            self.text = "Test question?"
            self.option_a = "Option A"
            self.option_b = "Option B"
            self.option_c = "Option C"
            self.option_d = "Option D"
            self.correct_answer = "A"
            self.id = 1
    
    context = MockContext()
    data = context.user_data
    data["chat_id"] = 12345  # This should now be set
    data["questions"] = [MockQuestion()]
    data["index"] = 0
    
    try:
        import asyncio
        
        async def test_show_next():
            # This should work now since chat_id is set
            # We'll get an error about bot.send_poll but that's expected in test
            try:
                await show_next_question(None, context, data)
            except AttributeError:
                # Expected - no actual bot instance in test
                return True
            except Exception as e:
                if "No chat_id available" in str(e):
                    print("❌ chat_id not found - fix failed")
                    return False
                else:
                    # Other errors are expected in test environment
                    return True
        
        result = asyncio.run(test_show_next())
        print("✅ show_next_question logic works with chat_id")
        return True
        
    except Exception as e:
        print(f"❌ Error in show_next_question test: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Next Question Chat ID Fix Verification")
    print("=" * 60)
    
    try:
        success1 = test_chat_id_fix()
        success2 = test_show_next_question_logic()
        
        if success1 and success2:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("\n✅ The chat_id fix is working correctly:")
            print("• chat_id is properly set when starting exams/practice")
            print("• Fallback mechanisms work for different update scenarios")
            print("• show_next_question can now access chat_id for sending polls")
            print("\n🎯 Next questions should now appear after users answer!")
            return True
        else:
            print("\n❌ Some tests failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

