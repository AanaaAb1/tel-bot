t #!/usr/bin/env python3
"""
Debug the chapter selection keyboard button count
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.keyboards.admin_question_keyboard import get_admin_chapter_selection_keyboard

def debug_chapter_keyboard():
    """Debug the chapter selection keyboard to see what buttons are generated"""
    print("🔍 DEBUGGING CHAPTER SELECTION KEYBOARD")
    print("=" * 50)
    
    keyboard = get_admin_chapter_selection_keyboard()
    
    print("Buttons in keyboard:")
    total_buttons = 0
    
    for i, row in enumerate(keyboard.inline_keyboard):
        print(f"Row {i+1}: {len(row)} buttons")
        for j, button in enumerate(row):
            print(f"  Button {j+1}: '{button.text}' -> {button.callback_data}")
            total_buttons += 1
    
    print(f"\nTotal buttons: {total_buttons}")
    
    # Expected buttons:
    expected = [
        "📖 Chapter 1", "📖 Chapter 2", "📖 Chapter 3", "📖 Chapter 4", "📖 Chapter 5",
        "📖 Chapter 6", "📖 Chapter 7", "📖 Chapter 8", "📖 Chapter 9", "📖 Chapter 10",
        "🚫 No Chapter", "⬅️ Back to Course Selection"
    ]
    
    print(f"Expected buttons: {len(expected)}")
    print(f"Expected: {expected}")

if __name__ == "__main__":
    debug_chapter_keyboard()
