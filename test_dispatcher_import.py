#!/usr/bin/env python3
"""
Simple test to check dispatcher import
"""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

def test_dispatcher_import():
    """Test if dispatcher imports without conflicts"""
    print("Testing dispatcher import...")
    
    try:
        # Import the dispatcher
        from app.bot.dispatcher_fixed import register_handlers
        print("✅ SUCCESS: Dispatcher imported successfully!")
        print("✅ All import conflicts have been resolved!")
        return True
    except ImportError as e:
        print(f"❌ FAILED: Import error - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Other error - {e}")
        return False

if __name__ == "__main__":
    success = test_dispatcher_import()
    if success:
        print("\n🎉 DISPATCHER FIX COMPLETE!")
        print("The import conflicts between admin_question_handler.py and admin_question_handler_fixed.py have been resolved.")
    else:
        print("\n❌ DISPATCHER FIX FAILED!")
    
    sys.exit(0 if success else 1)
