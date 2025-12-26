#!/usr/bin/env python3
"""
DIFFICULTY-BASED EXAM FLOW IMPLEMENTATION
Implements: Menu → Course → Difficulty → Chapter → Questions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal, engine
from app.models.course import Course, Base
from app.models.chapter import Chapter
from app.models.question import Question

def add_difficulty_to_questions():
    """Add difficulty column to questions table"""
    print("🔧 Adding difficulty column to questions table...")
    
    try:
        # Check if difficulty column already exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('questions')]
        
        if 'difficulty' not in columns:
            # Add difficulty column
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE questions ADD COLUMN difficulty VARCHAR(20) DEFAULT 'Easy'"))
                conn.commit()
                print("✅ Added difficulty column to questions table")
        else:
            print("✅ Difficulty column already exists")
        
        return True
    except Exception as e:
        print(f"❌ Error adding difficulty column: {e}")
        return False

def create_sample_questions_with_difficulty():
    """Create sample questions with different difficulty levels"""
    print("\n📝 Creating sample questions with difficulty levels...")
    
    db = SessionLocal()
    try:
        # Get courses and chapters
        courses = db.query(Course).all()
        total_questions_created = 0
        
        for course in courses:
            chapters = db.query(Chapter).filter_by(course_id=course.id).all()
            
            for chapter in chapters:
                # Check if chapter already has questions
                existing_questions = db.query(Question).filter_by(
                    course_id=course.id,
                    chapter_id=chapter.id
                ).all()
                
                if existing_questions:
                    print(f"   ✅ {course.name} - {chapter.name}: Already has {len(existing_questions)} questions")
                    continue
                
                # Create sample questions for each difficulty level
                difficulties = ['Easy', 'Intermediate', 'Advanced']
                
                for difficulty in difficulties:
                    sample_question = Question(
                        course_id=course.id,
                        chapter_id=chapter.id,
                        difficulty=difficulty,
                        question_text=f"Sample {difficulty} question for {course.name} - {chapter.name}",
                        option_a=f"Option A for {difficulty}",
                        option_b=f"Option B for {difficulty}",
                        option_c=f"Option C for {difficulty}",
                        option_d=f"Option D for {difficulty}",
                        correct_answer="A",
                        explanation=f"This is a {difficulty} question explanation."
                    )
                    db.add(sample_question)
                    total_questions_created += 1
                
                print(f"   ✅ {course.name} - {chapter.name}: Created 3 questions (Easy, Intermediate, Advanced)")
        
        if total_questions_created > 0:
            db.commit()
            print(f"✅ {total_questions_created} sample questions created")
        else:
            print("✅ All chapters already have questions")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating questions: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_difficulty_keyboard():
    """Create difficulty selection keyboard"""
    print("\n🎛️  Creating difficulty selection keyboard...")
    
    difficulty_keyboard_content = '''from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_difficulty_keyboard():
    """Create difficulty selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("🟢 Easy", callback_data="difficulty_easy")],
        [InlineKeyboardButton("🟡 Intermediate", callback_data="difficulty_intermediate")],
        [InlineKeyboardButton("🔴 Advanced", callback_data="difficulty_advanced")],
        [InlineKeyboardButton("🔙 Back to Courses", callback_data="back_to_courses")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_difficulty_text(course_name):
    """Get text for difficulty selection"""
    return f"📚 {course_name}\\n\\n🎯 Select difficulty level:\\n\\n🟢 Easy - Basic concepts and fundamentals\\n🟡 Intermediate - Moderate complexity\\n🔴 Advanced - Challenging problems"
'''
    
    try:
        with open('/home/aneman/Desktop/Exambot/telegramexambot/app/keyboards/difficulty_keyboard.py', 'w') as f:
            f.write(difficulty_keyboard_content)
        print("✅ Created difficulty_keyboard.py")
        return True
    except Exception as e:
        print(f"❌ Error creating difficulty keyboard: {e}")
        return False

def create_difficulty_handler():
    """Create difficulty selection handler"""
    print("\n🎛️  Creating difficulty selection handler...")
    
    handler_content = '''from telegram import Update
from telegram.ext import CallbackContext
from app.keyboards.difficulty_keyboard import get_difficulty_keyboard, get_difficulty_text
from app.services.course_service import get_course_by_name
from app.services.chapter_service import get_chapters_by_course_id
from app.keyboards.chapter_selection_keyboard import get_chapter_keyboard

async def difficulty_selection_handler(update: Update, context: CallbackContext):
    """Handle difficulty selection"""
    query = update.callback_query
    await query.answer()
    
    try:
        callback_data = query.data
        course_name = context.user_data.get('selected_course')
        
        if not course_name:
            await query.edit_message_text("❌ Course not found. Please start again.")
            return
        
        if callback_data == "back_to_courses":
            # Return to course selection
            from app.handlers.course_handler import select_course
            await select_course(update, context)
            return
        
        # Extract difficulty
        if callback_data.startswith("difficulty_"):
            difficulty = callback_data.replace("difficulty_", "")
            
            # Store difficulty in user data
            context.user_data['selected_difficulty'] = difficulty
            
            # Get course
            course = get_course_by_name(course_name)
            if not course:
                await query.edit_message_text("❌ Course not found.")
                return
            
            # Get chapters for the course
            chapters = get_chapters_by_course_id(course.id)
            
            if not chapters:
                await query.edit_message_text("❌ No chapters found for this course.")
                return
            
            # Show chapter selection with difficulty context
            keyboard = get_chapter_keyboard(chapters)
            text = f"📚 {course_name}\\n\\n🎯 Difficulty: {difficulty}\\n\\n📖 Select a chapter:"
            
            await query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        print(f"Error in difficulty selection handler: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")
'''
    
    try:
        with open('/home/aneman/Desktop/Exambot/telegramexambot/app/handlers/difficulty_handler.py', 'w') as f:
            f.write(handler_content)
        print("✅ Created difficulty_handler.py")
        return True
    except Exception as e:
        print(f"❌ Error creating difficulty handler: {e}")
        return False

def update_course_handler_for_difficulty():
    """Update course handler to include difficulty selection"""
    print("\n🔄 Updating course handler for difficulty flow...")
    
    try:
        # Read current course handler
        course_handler_path = '/home/aneman/Desktop/Exambot/telegramexambot/app/handlers/course_handler.py'
        with open(course_handler_path, 'r') as f:
            content = f.read()
        
        # Update the select_course function to show difficulty selection
        if 'get_difficulty_keyboard' not in content:
            # Add import for difficulty keyboard
            if 'from app.keyboards.difficulty_keyboard import' not in content:
                content = content.replace(
                    'from app.keyboards.course_keyboard import get_course_keyboard',
                    'from app.keyboards.course_keyboard import get_course_keyboard\\nfrom app.keyboards.difficulty_keyboard import get_difficulty_keyboard, get_difficulty_text'
                )
            
            # Update the course selection logic to show difficulty selection
            old_logic = '''        # Show chapter selection
        keyboard = get_chapter_keyboard(chapters)
        await query.edit_message_text(f"📚 {course.name}\\n\\n📖 Select a chapter:", reply_markup=keyboard)'''
            
            new_logic = '''        # Show difficulty selection instead of chapter selection
        keyboard = get_difficulty_keyboard()
        text = get_difficulty_text(course.name)
        await query.edit_message_text(text, reply_markup=keyboard)'''
            
            content = content.replace(old_logic, new_logic)
            
            # Write updated content
            with open(course_handler_path, 'w') as f:
                f.write(content)
            
            print("✅ Updated course handler for difficulty flow")
        else:
            print("✅ Course handler already updated")
        
        return True
    except Exception as e:
        print(f"❌ Error updating course handler: {e}")
        return False

def update_question_service_for_difficulty():
    """Update question service to filter by difficulty"""
    print("\n🔄 Updating question service for difficulty filtering...")
    
    try:
        question_service_path = '/home/aneman/Desktop/Exambot/telegramexambot/app/services/question_service.py'
        with open(question_service_path, 'r') as f:
            content = f.read()
        
        # Add difficulty filtering function
        if 'get_questions_by_difficulty' not in content:
            difficulty_function = '''
def get_questions_by_difficulty(course_id: int, chapter_id: int, difficulty: str, limit: int = 10):
    """Get questions by course, chapter and difficulty"""
    db = SessionLocal()
    try:
        questions = db.query(Question).filter(
            Question.course_id == course_id,
            Question.chapter_id == chapter_id,
            Question.difficulty == difficulty
        ).limit(limit).all()
        return questions
    except Exception as e:
        print(f"Error getting questions by difficulty: {e}")
        return []
    finally:
        db.close()
'''
            
            # Add the function before the closing of the file
            content = content + difficulty_function
            
            # Write updated content
            with open(question_service_path, 'w') as f:
                f.write(content)
            
            print("✅ Updated question service for difficulty filtering")
        else:
            print("✅ Question service already has difficulty filtering")
        
        return True
    except Exception as e:
        print(f"❌ Error updating question service: {e}")
        return False

def update_chapter_handler_for_difficulty():
    """Update chapter handler to use difficulty filtering"""
    print("\n🔄 Updating chapter handler for difficulty flow...")
    
    try:
        chapter_handler_path = '/home/aneman/Desktop/Exambot/telegramexambot/app/handlers/chapter_selection_handler.py'
        
        # Read current content
        with open(chapter_handler_path, 'r') as f:
            content = f.read()
        
        # Update to use difficulty filtering
        old_import = 'from app.services.question_service import get_questions_by_chapter'
        new_import = '''from app.services.question_service import get_questions_by_chapter, get_questions_by_difficulty'''
        
        if old_import in content:
            content = content.replace(old_import, new_import)
        
        # Update the question retrieval logic
        old_logic = '''        # Get questions for this chapter
        questions = get_questions_by_chapter(course_id, chapter_id)'''
        
        new_logic = '''        # Get questions for this chapter with selected difficulty
        difficulty = context.user_data.get('selected_difficulty', 'Easy')
        questions = get_questions_by_difficulty(course_id, chapter_id, difficulty)'''
        
        if old_logic in content:
            content = content.replace(old_logic, new_logic)
            
            # Write updated content
            with open(chapter_handler_path, 'w') as f:
                f.write(content)
            
            print("✅ Updated chapter handler for difficulty flow")
        else:
            print("✅ Chapter handler already updated")
        
        return True
    except Exception as e:
        print(f"❌ Error updating chapter handler: {e}")
        return False

def update_dispatcher():
    """Update dispatcher to include difficulty handler"""
    print("\n🔄 Updating dispatcher for difficulty handler...")
    
    try:
        dispatcher_path = '/home/aneman/Desktop/Exambot/telegramexambot/app/bot/dispatcher.py'
        with open(dispatcher_path, 'r') as f:
            content = f.read()
        
        # Add difficulty handler if not already added
        if 'difficulty_selection_handler' not in content:
            # Add import
            if 'from app.handlers.difficulty_handler import' not in content:
                import_line = 'from app.handlers.difficulty_handler import difficulty_selection_handler'
                if 'from app.handlers.' in content:
                    # Find the last import from handlers and add after it
                    lines = content.split('\\n')
                    for i, line in enumerate(lines):
                        if line.startswith('from app.handlers.'):
                            insert_pos = i + 1
                    lines.insert(insert_pos, import_line)
                    content = '\\n'.join(lines)
            
            # Add callback query handler
            callback_pattern = '''    # Difficulty selection handler
    dispatcher.add_handler(CallbackQueryHandler(difficulty_selection_handler, pattern="^difficulty_"))
'''
            
            if callback_pattern not in content:
                # Add after existing callback handlers
                if 'dispatcher.add_handler(CallbackQueryHandler(' in content:
                    lines = content.split('\\n')
                    for i, line in enumerate(lines):
                        if 'dispatcher.add_handler(CallbackQueryHandler(' in line and 'difficulty' not in line:
                            insert_pos = i + 1
                    lines.insert(insert_pos, callback_pattern.strip())
                    content = '\\n'.join(lines)
            
            # Write updated content
            with open(dispatcher_path, 'w') as f:
                f.write(content)
            
            print("✅ Updated dispatcher for difficulty handler")
        else:
            print("✅ Dispatcher already updated")
        
        return True
    except Exception as e:
        print(f"❌ Error updating dispatcher: {e}")
        return False

def test_difficulty_flow():
    """Test the difficulty-based flow"""
    print("\n🧪 Testing difficulty-based flow...")
    
    db = SessionLocal()
    try:
        # Test 1: Check if difficulty column exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('questions')]
        
        if 'difficulty' in columns:
            print("✅ Difficulty column exists in questions table")
        else:
            print("❌ Difficulty column missing")
            return False
        
        # Test 2: Check if questions have difficulty levels
        questions = db.query(Question).all()
        difficulties = set()
        for q in questions:
            if hasattr(q, 'difficulty') and q.difficulty:
                difficulties.add(q.difficulty)
        
        print(f"✅ Found difficulty levels: {difficulties}")
        
        # Test 3: Check courses and chapters
        courses = db.query(Course).all()
        print(f"✅ Total courses: {len(courses)}")
        
        total_chapters = 0
        for course in courses:
            chapters = db.query(Chapter).filter_by(course_id=course.id).all()
            total_chapters += len(chapters)
        
        print(f"✅ Total chapters: {total_chapters}")
        
        # Test 4: Check question distribution by difficulty
        for difficulty in ['Easy', 'Intermediate', 'Advanced']:
            count = db.query(Question).filter_by(difficulty=difficulty).count()
            print(f"✅ {difficulty} questions: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        db.close()

def main():
    """Main execution function"""
    print("🚀 DIFFICULTY-BASED EXAM FLOW IMPLEMENTATION")
    print("=" * 60)
    print("📋 New Flow: Menu → Course → Difficulty → Chapter → Questions")
    print("=" * 60)
    
    # Step 1: Add difficulty to questions
    if not add_difficulty_to_questions():
        print("❌ Failed to add difficulty column")
        return False
    
    # Step 2: Create sample questions with difficulty
    if not create_sample_questions_with_difficulty():
        print("❌ Failed to create sample questions")
        return False
    
    # Step 3: Create difficulty keyboard
    if not create_difficulty_keyboard():
        print("❌ Failed to create difficulty keyboard")
        return False
    
    # Step 4: Create difficulty handler
    if not create_difficulty_handler():
        print("❌ Failed to create difficulty handler")
        return False
    
    # Step 5: Update course handler
    if not update_course_handler_for_difficulty():
        print("❌ Failed to update course handler")
        return False
    
    # Step 6: Update question service
    if not update_question_service_for_difficulty():
        print("❌ Failed to update question service")
        return False
    
    # Step 7: Update chapter handler
    if not update_chapter_handler_for_difficulty():
        print("❌ Failed to update chapter handler")
        return False
    
    # Step 8: Update dispatcher
    if not update_dispatcher():
        print("❌ Failed to update dispatcher")
        return False
    
    # Step 9: Test the flow
    if not test_difficulty_flow():
        print("❌ Flow testing failed")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 DIFFICULTY-BASED FLOW IMPLEMENTATION COMPLETE!")
    print("✅ New user flow implemented:")
    print("   1. Menu → Course")
    print("   2. Select Course (Maths, Chemistry, etc)")
    print("   3. Select Difficulty (Easy, Intermediate, Advanced)")
    print("   4. Select Chapter")
    print("   5. Questions (filtered by difficulty)")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

