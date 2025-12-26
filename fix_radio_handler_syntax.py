#!/usr/bin/env python3
"""
Fix the syntax error in radio_question_handler.py
"""

def fix_syntax_error():
    """Fix the f-string syntax error in radio_question_handler.py"""
    
    file_path = "/home/aneman/Desktop/Exambot/telegramexambot/app/handlers/radio_question_handler.py"
    
    # Read the current file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic line and fix it
    lines = content.split('\n')
    
    # Look for the line with the unterminated f-string
    for i, line in enumerate(lines):
        if 'f"📝 Question {question_number}/{total_questions} ({timer_text})' in line and not line.strip().endswith('",'):
            # This is the broken line, let's fix it
            lines[i] = '        "question": f"📝 Question {question_number}/{total_questions} ({timer_text})\\n\\n{question.text}",'
            break
    
    # Write back the fixed content
    fixed_content = '\n'.join(lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Fixed syntax error in radio_question_handler.py")

if __name__ == "__main__":
    fix_syntax_error()
