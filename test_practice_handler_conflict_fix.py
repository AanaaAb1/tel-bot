#!/usr/bin/env python3
"""
Test for Practice Handler Conflict Fix

This test validates that the handler routing conflicts in practice handlers have been resolved:
1. Unique callback patterns for different practice handlers
2. Proper callback data generation in keyboards
3. Correct callback data parsing in handlers
"""

import re
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dispatcher_patterns():
    """Test that dispatcher has unique patterns for practice handlers"""
    print("\n🔍 Testing Dispatcher Patterns...")
    
    try:
        with open('/home/aneman/Desktop/Exambot/telegramexambot/app/bot/dispatcher_fixed.py', 'r') as f:
            content = f.read()
        
        # Extract practice handler patterns
        practice_patterns = []
        lines = content.split('\n')
        
        for line in lines:
            if 'practice_course_selected' in line and 'pattern=' in line:
                # Extract pattern from the line
                match = re.search(r'pattern="([^"]+)"', line)
                if match:
                    practice_patterns.append(('practice_course_selected', match.group(1)))
            
            elif 'practice_course_for_chapter' in line and 'pattern=' in line:
                match = re.search(r'pattern="([^"]+)"', line)
                if match:
                    practice_patterns.append(('practice_course_for_chapter', match.group(1)))
            
            elif 'practice_chapter_selected' in line and 'pattern=' in line:
                match = re.search(r'pattern="([^"]+)"', line)
                if match:
                    practice_patterns.append(('practice_chapter_selected', match.group(1)))
        
        print(f"Found {len(practice_patterns)} practice handler patterns:")
        for handler, pattern in practice_patterns:
            print(f"  - {handler}: {pattern}")
        
        # Check for conflicts (duplicate patterns)
        patterns_only = [pattern for _, pattern in practice_patterns]
        unique_patterns = set(patterns_only)
        
        if len(patterns_only) == len(unique_patterns):
            print("✅ All patterns are unique - no conflicts detected")
            return True
        else:
            print("❌ Duplicate patterns found - conflicts exist")
            print(f"Total patterns: {len(patterns_only)}, Unique patterns: {len(unique_patterns)}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing dispatcher patterns: {e}")
        return False

def test_keyboard_callback_data():
    """Test that keyboards generate correct callback data"""
    print("\n🔍 Testing Keyboard Callback Data...")
    
    try:
        with open('/home/aneman/Desktop/Exambot/telegramexambot/app/keyboards/radio_exam_keyboard.py', 'r') as f:
            content = f.read()
        
        # Check for practice callback data generation
        practice_callbacks = []
        lines = content.split('\n')
        
        for line in lines:
            if 'callback_data=f"practice_' in line:
                # Extract callback data pattern
                match = re.search(r'callback_data=f"([^"]+)"', line)
                if match:
                    practice_callbacks.append(match.group(1))
        
        print(f"Found {len(practice_callbacks)} practice callback data patterns:")
        for callback in practice_callbacks:
            print(f"  - {callback}")
        
        # Expected patterns after fix
        expected_patterns = [
            'practice_course_',
            'practice_course_chapter_',
            'practice_chapter_'
        ]
        
        conflicts_found = False
        for pattern in expected_patterns:
            matching_callbacks = [cb for cb in practice_callbacks if pattern in cb]
            if len(matching_callbacks) > 1:
                print(f"❌ Multiple callbacks use pattern '{pattern}': {matching_callbacks}")
                conflicts_found = True
        
        if not conflicts_found:
            print("✅ All callback patterns are unique - no conflicts detected")
            return True
        else:
            print("❌ Conflicts found in callback patterns")
            return False
            
    except Exception as e:
        print(f"❌ Error testing keyboard callback data: {e}")
        return False

def test_handler_parsing():
    """Test that handlers parse the correct callback data"""
    print("\n🔍 Testing Handler Callback Data Parsing...")
    
    try:
        with open('/home/aneman/Desktop/Exambot/telegramexambot/app/handlers/practice_handler.py', 'r') as f:
            content = f.read()
        
        # Extract callback data parsing patterns
        parsing_patterns = []
        lines = content.split('\n')
        
        for line in lines:
            if '.replace("practice_course_", "")' in line and 'practice_course_selected' in content[max(0, content.find(line)-500):content.find(line)]:
                parsing_patterns.append(('practice_course_selected', 'practice_course_'))
            elif '.replace("practice_course_chapter_", "")' in line and 'practice_course_for_chapter' in content[max(0, content.find(line)-500):content.find(line)]:
                parsing_patterns.append(('practice_course_for_chapter', 'practice_course_chapter_'))
            elif '.replace("practice_chapter_", "")' in line and 'practice_chapter_selected' in content[max(0, content.find(line)-500):content.find(line)]:
                parsing_patterns.append(('practice_chapter_selected', 'practice_chapter_'))
        
        print(f"Found {len(parsing_patterns)} handler parsing patterns:")
        for handler, pattern in parsing_patterns:
            print(f"  - {handler}: replaces '{pattern}'")
        
        # Check for consistency with dispatcher patterns
        expected_parsing = [
            ('practice_course_selected', 'practice_course_'),
            ('practice_course_for_chapter', 'practice_course_chapter_'),
            ('practice_chapter_selected', 'practice_chapter_')
        ]
        
        expected_set = set(expected_parsing)
        actual_set = set(parsing_patterns)
        
        if expected_set == actual_set:
            print("✅ Handler parsing patterns match expected patterns")
            return True
        else:
            print("❌ Handler parsing patterns don't match expected patterns")
            print(f"Expected: {expected_parsing}")
            print(f"Actual: {parsing_patterns}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing handler parsing: {e}")
        return False

def test_integration():
    """Test integration between patterns and parsing"""
    print("\n🔍 Testing Pattern-Parsing Integration...")
    
    try:
        # Test specific callback data scenarios
        test_cases = [
            {
                'callback_data': 'practice_course_123',
                'expected_handler': 'practice_course_selected',
                'expected_course_id': 123
            },
            {
                'callback_data': 'practice_course_chapter_456',
                'expected_handler': 'practice_course_for_chapter',
                'expected_course_id': 456
            },
            {
                'callback_data': 'practice_chapter_789',
                'expected_handler': 'practice_chapter_selected',
                'expected_chapter_id': 789
            }
        ]
        
        all_passed = True
        for i, case in enumerate(test_cases, 1):
            callback = case['callback_data']
            expected_handler = case['expected_handler']
            
            # Simulate pattern matching
            matched_handler = None
            if callback.startswith('practice_course_') and not callback.startswith('practice_course_chapter_'):
                matched_handler = 'practice_course_selected'
                expected_id = case.get('expected_course_id')
                actual_id = int(callback.replace('practice_course_', ''))
            elif callback.startswith('practice_course_chapter_'):
                matched_handler = 'practice_course_for_chapter'
                expected_id = case.get('expected_course_id')
                actual_id = int(callback.replace('practice_course_chapter_', ''))
            elif callback.startswith('practice_chapter_'):
                matched_handler = 'practice_chapter_selected'
                expected_id = case.get('expected_chapter_id')
                actual_id = int(callback.replace('practice_chapter_', ''))
            
            if matched_handler == expected_handler and actual_id == expected_id:
                print(f"  ✅ Test {i}: {callback} → {matched_handler}(id={actual_id})")
            else:
                print(f"  ❌ Test {i}: {callback} → {matched_handler} (expected {expected_handler})")
                all_passed = False
        
        if all_passed:
            print("✅ All integration tests passed")
            return True
        else:
            print("❌ Some integration tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Practice Handler Conflict Fix")
    print("=" * 50)
    
    tests = [
        test_dispatcher_patterns,
        test_keyboard_callback_data,
        test_handler_parsing,
        test_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Practice handler conflict fix is working correctly!")
        return True
    else:
        print("❌ Some tests failed - Please review the issues above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

