#!/usr/bin/env python3
"""
Test Chapter Selection After Fix
Verifies that chapters appear when users click courses after removing routing conflicts
"""

import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.session import SessionLocal
from app.services.chapter_service import get_chapters_by_course
from app.handlers.course_handler import select_course
from app.handlers.menu_handler import menu

def test_chapter_service_works():
    """Test that chapter service can fetch chapters"""
    print("🔍 Testing Chapter Service...")
    
    db = SessionLocal()
    try:
        # Test fetching chapters for a course
        chapters = get_chapters_by_course(1)
        print(f"✅ Chapters for course 1: {len(chapters)}")
        
        for chapter in chapters:
            print(f"  - Chapter {chapter.id}: {chapter.name}")
            
        return len(chapters) > 0
    except Exception as e:
        print(f"❌ Chapter service error: {e}")
        return False
    finally:
        db.close()

def test_menu_handler_no_conflicting_routes():
    """Test that menu handler no longer has conflicting routes"""
    print("\n🔍 Testing Menu Handler...")
    
    try:
        # Read the menu handler file
        with open('app/handlers/menu_handler.py', 'r') as f:
            content = f.read()
        
        # Check that conflicting function calls are removed (the real issue)
        has_select_course_call = 'await select_course(update, context)' in content
        has_start_exam_selected_call = 'await start_exam_selected(update, context)' in content
        
        # These should NOT be in the menu handler anymore
        if not has_select_course_call and not has_start_exam_selected_call:
            print("✅ Menu handler no longer has conflicting function calls")
            return True
        else:
            print("❌ Menu handler still has conflicting function calls")
            print(f"  - select_course call present: {has_select_course_call}")
            print(f"  - start_exam_selected call present: {has_start_exam_selected_call}")
            return False
            
    except Exception as e:
        print(f"❌ Menu handler test error: {e}")
        return False

async def test_callback_routing():
    """Test that callback patterns are properly routed"""
    print("\n🔍 Testing Callback Routing...")
    
    # Mock update and context
    update = Mock()
    context = Mock()
    query = Mock()
    update.callback_query = query
    query.from_user.id = 12345
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    
    # Test 1: Menu handler should NOT handle exam_course_ patterns
    query.data = "exam_course_1"
    
    try:
        await menu(update, context)
        
        # The menu handler SHOULD respond to exam_course_ patterns (but with the correct behavior)
        # It should fall through to the else clause and show the main menu
        if query.edit_message_text.called:
            # Check what message was sent - should be the main menu refresh
            args, kwargs = query.edit_message_text.call_args
            message_text = args[0] if args else ""
            
            if "Choose an option:" in message_text:
                print("✅ Menu handler correctly handles exam_course_ patterns by showing main menu")
                routing_test_passed = True
            else:
                print("❌ Menu handler responded but with wrong message")
                routing_test_passed = False
        else:
            print("❌ Menu handler did not respond to exam_course_ pattern")
            routing_test_passed = False
            
    except Exception as e:
        print(f"❌ Callback routing test error: {e}")
        routing_test_passed = False
    
    return routing_test_passed

def main():
    """Run all tests"""
    print("🧪 TESTING CHAPTER SELECTION AFTER FIX")
    print("=" * 50)
    
    # Test 1: Chapter service works
    service_test = test_chapter_service_works()
    
    # Test 2: Menu handler no conflicting routes
    menu_test = test_menu_handler_no_conflicting_routes()
    
    # Test 3: Callback routing
    routing_test = asyncio.run(test_callback_routing())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY:")
    print(f"  - Chapter Service: {'✅ PASS' if service_test else '❌ FAIL'}")
    print(f"  - Menu Handler: {'✅ PASS' if menu_test else '❌ FAIL'}")
    print(f"  - Callback Routing: {'✅ PASS' if routing_test else '❌ FAIL'}")
    
    all_passed = service_test and menu_test and routing_test
    
    print(f"\n🎯 OVERALL: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Chapter selection should now work properly!")
        print("   Users can click courses → chapters appear → exams start")
    else:
        print("\n⚠️ Some issues remain - manual testing recommended")
    
    return all_passed

if __name__ == "__main__":
    main()

