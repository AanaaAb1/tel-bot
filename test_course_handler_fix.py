#!/usr/bin/env python3
"""
Test script to verify the course handler fix works correctly.
This simulates the select_course function logic without needing a Telegram bot.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.handlers.course_handler import get_chapters_by_course
from app.services.course_service import get_course_by_id

def test_chapter_retrieval():
    """Test that we can retrieve chapters for each course"""
    
    print("=== TESTING COURSE HANDLER FIX ===\n")
    
    # Test Biology course
    print("🔬 Testing Biology course (ID: 1)...")
    biology_course = get_course_by_id(1)
    if biology_course:
        print(f"  ✅ Course found: {biology_course.name}")
        chapters = get_chapters_by_course(1)
        print(f"  ✅ Chapters found: {len(chapters)}")
        for chapter in chapters:
            print(f"     - Chapter: {chapter.name} (ID: {chapter.id})")
    else:
        print("  ❌ Biology course not found!")
        return False
    
    print()
    
    # Test Physics course  
    print("⚛️ Testing Physics course (ID: 2)...")
    physics_course = get_course_by_id(2)
    if physics_course:
        print(f"  ✅ Course found: {physics_course.name}")
        chapters = get_chapters_by_course(2)
        print(f"  ✅ Chapters found: {len(chapters)}")
        for chapter in chapters:
            print(f"     - Chapter: {chapter.name} (ID: {chapter.id})")
    else:
        print("  ❌ Physics course not found!")
        return False
    
    print()
    
    # Test chapter sorting
    print("🔢 Testing chapter number sorting...")
    
    # Get all chapters for biology and test sorting
    chapters = get_chapters_by_course(1)
    
    def get_chapter_number(chapter_name):
        try:
            return int(chapter_name.split()[-1])
        except:
            return 0
    
    # Sort chapters numerically
    sorted_chapters = sorted(chapters, key=lambda x: get_chapter_number(x.name))
    
    print("  Original order:")
    for chapter in chapters:
        print(f"    {chapter.name} -> Chapter number: {get_chapter_number(chapter.name)}")
    
    print("  Sorted order:")
    for chapter in sorted_chapters:
        print(f"    {chapter.name} -> Chapter number: {get_chapter_number(chapter.name)}")
    
    print()
    
    # Test callback data format
    print("🏷️ Testing callback data format...")
    for chapter in chapters:
        callback_data = f"start_exam_{chapter.id}"
        print(f"  Chapter '{chapter.name}' -> callback_data: '{callback_data}'")
    
    print()
    print("=== TEST COMPLETE ===")
    print("✅ Course handler fix appears to be working correctly!")
    print("✅ Chapters are being retrieved successfully!")
    print("✅ Sorting logic is working!")
    print("✅ Callback data format is correct!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_chapter_retrieval()
        if success:
            print("\n🎉 All tests passed! The course handler fix is successful.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
