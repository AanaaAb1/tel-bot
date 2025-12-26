#!/usr/bin/env python3
"""
Complete rewrite of the radio_question_handler.py file to fix syntax errors
"""

def fix_radio_handler_complete():
    """Completely rewrite the radio_question_handler.py file with proper syntax"""
    
    file_path = "/home/aneman/Desktop/Exambot/telegramexambot/app/handlers/radio_question_handler.py"
    
    # Read the current file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic return statement and replace it
    old_return_pattern = r'return \{\s*"question": f"📝 Question \{question_number\}/\{total_questions\} \(⏰ \{get_timer_duration\(course_name\)//60\} minute.*?question_id": question\.id\s*\}'
    
    # Create the corrected return statement
    new_return = '''    # Get timer duration for this course
    timer_duration = get_timer_duration(course_name)
    timer_text = f"⏰ {timer_duration//60} minute{'s' if timer_duration > 60 else ''}"
    
    return {
        "question": f"📝 Question {question_number}/{total_questions} ({timer_text})\\n\\n{question.text}",
        "options": labeled_options,
        "correct_option_id": correct_option_id,
        "question_id": question.id,
        "timer_duration": timer_duration
    }'''
    
    # Use a more specific replacement pattern
    import re
    
    # Find and replace the return statement more precisely
    lines = content.split('\n')
    new_lines = []
    in_return_block = False
    
    for i, line in enumerate(lines):
        if 'return {' in line and '"question":' in line:
            # Start of the return statement
            new_lines.append(new_return)
            # Skip the rest of the old return statement
            while i < len(lines) and '}' not in lines[i]:
                i += 1
            if i < len(lines):
                i += 1  # Skip the closing brace
            # Continue from the next line after the return block
            for j in range(i, len(lines)):
                if j < len(lines):
                    new_lines.append(lines[j])
            break
        else:
            new_lines.append(line)
    
    # Write the corrected content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Successfully fixed radio_question_handler.py syntax error")

if __name__ == "__main__":
    fix_radio_handler_complete()
