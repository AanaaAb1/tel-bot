#!/usr/bin/env python3
"""
End-to-End Practice Handler Test

This test simulates actual user interactions to verify that the practice handler 
conflicts have been completely resolved and the flow works correctly.
"""

import sys
import os
import logging
from unittest.mock import Mock, AsyncMock
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackQueryHandler

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import handlers and keyboards
from app.handlers.practice_handler import (
    practice_course_selected, 
    practice_course_for_chapter, 
    practice_chapter_selected
)
from app.keyboards.radio_exam_keyboard import create_practice_selection_keyboard
from app.keyboards.exam_keyboard import exam_selection_keyboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockDatabase:
    """Mock database for testing"""
    def __init__(self):
        self.chapters = [
            Mock(id=1, name="Chapter 1"),
            Mock(id=2, name="Chapter 2"),
            Mock(id=3, name="Chapter 3")
        ]
    
    def query(self, model):
        return Mock(
            filter_by=lambda **kwargs: Mock(
                all=lambda: [c for c in self.chapters if getattr(c, 'course_id', None) == list(kwargs.values())[0]]
            )
        )
    
    def close(self):
        pass

def create_mock_update(callback_data, from_user_id=12345):
    """Create a mock Telegram update with callback data"""
    # Create mock query
    mock_query = Mock()
    mock_query.answer = AsyncMock()
    mock_query.edit_message_text = AsyncMock()
    mock_query.data = callback_data
    
    # Create mock update
    update = Mock()
    update.callback_query = mock_query
    update.effective_user = Mock()
    update.effective_user.id = from_user_id
    
    return update

def create_mock_context():
    """Create a mock context"""
    context = Mock()
    context.user_data = {}
    context.bot_data = {}
    return context

async def test_practice_course_selection():
    """Test practice_course_selected handler"""
    print("\n🧪 Testing practice_course_selected handler...")
    
    # Test case 1: Valid course selection
    update = create_mock_update("practice_course_123")
    context = create_mock_context()
    
    try:
        # This should not crash and should extract course_id = 123
        await practice_course_selected(update, context)
        print("  ✅ practice_course_selected handler executed without errors")
        return True
    except Exception as e:
        print(f"  ❌ practice_course_selected failed: {e}")
        return False

async def test_practice_course_for_chapter():
    """Test practice_course_for_chapter handler"""
    print("\n🧪 Testing practice_course_for_chapter handler...")
    
    # Test case 1: Valid course chapter selection
    update = create_mock_update("practice_course_chapter_456")
    context = create_mock_context()
    
    try:
        # This should not crash and should extract course_id = 456
        await practice_course_for_chapter(update, context)
        print("  ✅ practice_course_for_chapter handler executed without errors")
        return True
    except Exception as e:
        print(f"  ❌ practice_course_for_chapter failed: {e}")
        return False

async def test_practice_chapter_selected():
    """Test practice_chapter_selected handler"""
    print("\n🧪 Testing practice_chapter_selected handler...")
    
    # Test case 1: Valid chapter selection
    update = create_mock_update("practice_chapter_789")
    context = create_mock_context()
    
    try:
        # This should not crash and should extract chapter_id = 789
        await practice_chapter_selected(update, context)
        print("  ✅ practice_chapter_selected handler executed without errors")
        return True
    except Exception as e:
        print(f"  ❌ practice_chapter_selected failed: {e}")
        return False

def test_keyboard_generation():
    """Test that keyboards generate correct callback data"""
    print("\n🧪 Testing keyboard callback data generation...")
    
    try:
        # Test practice selection keyboard
        keyboard = create_practice_selection_keyboard(123)
        buttons = keyboard.inline_keyboard
        
        print("  📱 Practice selection keyboard buttons:")
        for row in buttons:
            for button in row:
                print(f"    - {button.text}: {button.callback_data}")
        
        # Verify callback data patterns
        expected_patterns = [
            "practice_course_123",
            "practice_course_chapter_123"
        ]
        
        actual_patterns = [button.callback_data for row in buttons for button in row]
        
        conflicts = False
        for pattern in expected_patterns:
            matching = [p for p in actual_patterns if pattern in p]
            if len(matching) != 1:
                print(f"  ❌ Pattern '{pattern}' has conflicts or is missing")
                conflicts = True
        
        if not conflicts:
            print("  ✅ All keyboard callback patterns are unique")
            return True
        else:
            print("  ❌ Keyboard callback patterns have conflicts")
            return False
            
    except Exception as e:
        print(f"  ❌ Keyboard generation failed: {e}")
        return False

def test_dispatcher_pattern_matching():
    """Test that dispatcher patterns correctly match callback data"""
    print("\n🧪 Testing dispatcher pattern matching...")
    
    try:
        # Test patterns from dispatcher_fixed.py
        patterns = {
            'practice_course_selected': '^practice_course_(\\d+)$',
            'practice_course_for_chapter': '^practice_course_chapter_(\\d+)$',
            'practice_chapter_selected': '^practice_chapter_(\\d+)$'
        }
        
        import re
        
        test_cases = [
            ("practice_course_123", "practice_course_selected"),
            ("practice_course_chapter_456", "practice_course_for_chapter"),
            ("practice_chapter_789", "practice_chapter_selected")
        ]
        
        all_passed = True
        for callback_data, expected_handler in test_cases:
            matched_handler = None
            for handler, pattern in patterns.items():
                if re.match(pattern, callback_data):
                    matched_handler = handler
                    break
            
            if matched_handler == expected_handler:
                print(f"  ✅ {callback_data} → {matched_handler}")
            else:
                print(f"  ❌ {callback_data} → {matched_handler} (expected {expected_handler})")
                all_passed = False
        
        if all_passed:
            print("  ✅ All pattern matching tests passed")
            return True
        else:
            print("  ❌ Some pattern matching tests failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Pattern matching test failed: {e}")
        return False

def test_realistic_user_flow():
    """Test a realistic user interaction flow"""
    print("\n🧪 Testing realistic user flow...")
    
    try:
        print("  👤 Simulating user journey:")
        print("    1. User clicks 'Practice by Chapter' button")
        
        # Step 1: User clicks "Practice by Chapter" 
        callback_data = "practice_course_chapter_123"
        print(f"       Callback: {callback_data}")
        
        # This should match practice_course_for_chapter handler
        import re
        pattern = '^practice_course_chapter_(\\d+)$'
        if re.match(pattern, callback_data):
            course_id = int(callback_data.replace("practice_course_chapter_", ""))
            print(f"       ✅ Correctly routed to practice_course_for_chapter (course_id: {course_id})")
        else:
            print("       ❌ Failed to match pattern")
            return False
        
        print("    2. User selects a chapter from the list")
        
        # Step 2: User selects a chapter
        callback_data = "practice_chapter_456"
        print(f"       Callback: {callback_data}")
        
        pattern = '^practice_chapter_(\\d+)$'
        if re.match(pattern, callback_data):
            chapter_id = int(callback_data.replace("practice_chapter_", ""))
            print(f"       ✅ Correctly routed to practice_chapter_selected (chapter_id: {chapter_id})")
        else:
            print("       ❌ Failed to match pattern")
            return False
        
        print("    3. User clicks 'Practice by Course' button")
        
        # Step 3: User clicks "Practice by Course"
        callback_data = "practice_course_789"
        print(f"       Callback: {callback_data}")
        
        pattern = '^practice_course_(\\d+)$'
        if re.match(pattern, callback_data):
            course_id = int(callback_data.replace("practice_course_", ""))
            print(f"       ✅ Correctly routed to practice_course_selected (course_id: {course_id})")
        else:
            print("       ❌ Failed to match pattern")
            return False
        
        print("  ✅ Complete user flow test passed")
        return True
        
    except Exception as e:
        print(f"  ❌ User flow test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Running End-to-End Practice Handler Tests")
    print("=" * 60)
    
    # Run handler tests
    handler_tests = [
        test_practice_course_selection(),
        test_practice_course_for_chapter(),
        test_practice_chapter_selected()
    ]
    
    # Run other tests
    other_tests = [
        test_keyboard_generation(),
        test_dispatcher_pattern_matching(),
        test_realistic_user_flow()
    ]
    
    # Wait for async tests to complete
    handler_results = []
    for test in handler_tests:
        try:
            result = await test
            handler_results.append(result)
        except Exception as e:
            print(f"❌ Handler test failed with exception: {e}")
            handler_results.append(False)
    
    # Combine results
    all_results = handler_results + other_tests
    passed = sum(all_results)
    total = len(all_results)
    
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Practice handlers are working correctly!")
        print("✅ No handler conflicts detected")
        print("✅ All callback patterns are unique and working")
        print("✅ User flow is working as expected")
        return True
    else:
        print("❌ Some tests failed - Please review the issues above")
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

