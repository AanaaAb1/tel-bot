#!/usr/bin/env python3
"""
Minimal Test - Write results to file to bypass output capture issues
"""

import sys
import os
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test():
    """Run the test and write results to file"""
    results = []
    
    # Test 1: Basic Import
    try:
        from app.handlers.radio_question_handler import handle_poll_answer
        results.append("✅ Import test: PASSED")
    except Exception as e:
        results.append(f"❌ Import test: FAILED - {e}")
    
    # Test 2: Create Poll Question
    try:
        from app.handlers.radio_question_handler import create_poll_question
        
        question = Mock()
        question.id = 1
        question.text = "Test question?"
        question.option_a = "Option A"
        question.option_b = "Option B"
        question.option_c = None
        question.option_d = None
        question.correct_answer = "A"
        
        poll_data = create_poll_question(question, 1, 5)
        if len(poll_data['options']) == 2:
            results.append("✅ Create poll test: PASSED")
        else:
            results.append("❌ Create poll test: FAILED - Wrong option count")
    except Exception as e:
        results.append(f"❌ Create poll test: FAILED - {e}")
    
    # Test 3: Function Signatures
    try:
        import inspect
        from app.handlers.radio_question_handler import handle_poll_answer, show_next_question
        
        # Check handle_poll_answer
        handle_params = list(inspect.signature(handle_poll_answer).parameters.keys())
        if handle_params == ['update', 'context']:
            results.append("✅ handle_poll_answer signature: PASSED")
        else:
            results.append(f"❌ handle_poll_answer signature: FAILED - {handle_params}")
        
        # Check show_next_question
        next_params = list(inspect.signature(show_next_question).parameters.keys())
        if next_params == ['update', 'context', 'data']:
            results.append("✅ show_next_question signature: PASSED")
        else:
            results.append(f"❌ show_next_question signature: FAILED - {next_params}")
            
    except Exception as e:
        results.append(f"❌ Function signature test: FAILED - {e}")
    
    # Write results to file
    with open('test_results.txt', 'w') as f:
        f.write("RADIO QUESTION HANDLER SYNTAX FIX TEST RESULTS\n")
        f.write("=" * 50 + "\n\n")
        
        for result in results:
            f.write(result + "\n")
        
        f.write("\n" + "=" * 50 + "\n")
        
        passed = sum(1 for r in results if "✅" in r)
        total = len(results)
        
        f.write(f"Tests passed: {passed}/{total}\n")
        
        if passed == total:
            f.write("\n🎉 ALL TESTS PASSED!\n")
            f.write("The syntax error has been FIXED successfully.\n")
            f.write("The radio_question_handler.py file is now working correctly.\n")
        else:
            f.write(f"\n❌ {total - passed} tests failed\n")

if __name__ == "__main__":
    run_test()
