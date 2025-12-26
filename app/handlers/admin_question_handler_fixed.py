from app.database.session import SessionLocal
from app.models.question import Question
from app.keyboards.admin_question_keyboard import (
    get_admin_course_selection_keyboard,
    get_admin_chapter_selection_keyboard,
    get_admin_question_step_keyboard,
    get_admin_question_confirm_keyboard,
    get_admin_question_cancel_keyboard
)
from app.keyboards.admin_keyboard import get_admin_questions_menu
from app.config.constants import ADMIN_IDS
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging

logger = logging.getLogger(__name__)

# Helper function for safe message editing
async def safe_edit_message_text(update, text, reply_markup=None):
    """Safely edit a message with fallback to sending new message"""
    try:
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        else:
            # Fallback: send new message if no callback query
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error editing message: {e}")
        # Fallback: send new message if edit fails
        try:
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.message.reply_text(
                    text=text,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    text=text,
                    reply_markup=reply_markup
                )
        except Exception as fallback_error:
            print(f"Error in fallback message sending: {fallback_error}")

# Enhanced Admin Questions Menu
async def admin_questions_menu_enhanced(update, context):
    """Enhanced question management menu with new options"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    await safe_edit_message_text(update, 
        "❓ Question Management\n\nChoose an action:",
        reply_markup=get_admin_questions_menu()
    )

# Course Selection for Question Management
async def admin_select_course_for_question(update, context):
    """Handle course selection for question management"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    # Extract course from callback data
    callback_data = update.callback_query.data
    if callback_data == "admin_select_course_back":
        # Back to course selection
        await admin_questions_menu_enhanced(update, context)
        return

    if callback_data.startswith("admin_select_course_"):
        course = callback_data.replace("admin_select_course_", "")
        
        # Store selected course in user data
        context.user_data['admin_question_course'] = course
        
        # Show chapter selection
        course_display = course if course != "No Course" else "General Questions"
        await safe_edit_message_text(update, 
            f"📚 Selected Course: {course_display}\n\nNow select a chapter:",
            reply_markup=get_admin_chapter_selection_keyboard()
        )
    else:
        # Initial course selection
        await safe_edit_message_text(update, 
            "📚 Question Management - Course Selection\n\nPlease select a course:",
            reply_markup=get_admin_course_selection_keyboard()
        )

# Chapter Selection for Question Management
async def admin_select_chapter_for_question(update, context):
    """Handle chapter selection for question management"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    callback_data = update.callback_query.data
    
    if callback_data.startswith("admin_select_chapter_"):
        chapter = callback_data.replace("admin_select_chapter_", "")
        
        # Store selected chapter
        context.user_data['admin_question_chapter'] = chapter
        
        # Start question addition flow
        course = context.user_data.get('admin_question_course', 'Unknown')
        chapter_display = chapter if chapter != "No Chapter" else "General"
        
        await safe_edit_message_text(update, 
            f"📝 Adding question for {course} - {chapter_display}\n\n"
            f"Please send the question text:",
            reply_markup=get_admin_question_step_keyboard("question_text")
        )
        
        # Initialize question data
        context.user_data['admin_question_data'] = {
            'course': course,
            'chapter': chapter,
            'step': 'question_text',
            'text': '',
            'option_a': '',
            'option_b': '',
            'option_c': '',
            'option_d': '',
            'option_e': '',
            'correct_answer': 'A'  # Default
        }
        
        context.user_data['admin_question_flow'] = True

# Handle Question Addition Step
async def admin_handle_question_step(update, context):
    """Handle step-by-step question addition"""
    if update.effective_user.id not in ADMIN_IDS:
        return

    callback_data = update.callback_query.data
    
    if callback_data == "admin_question_done":
        # Move to next step
        await admin_move_to_next_question_step(update, context)
    elif callback_data == "admin_question_skip":
        # Skip optional step
        context.user_data['admin_question_data']['option_e'] = None
        await admin_move_to_next_question_step(update, context)
    elif callback_data == "admin_question_cancel":
        # Cancel the entire flow
        await admin_cancel_question_flow(update, context)
    elif callback_data == "admin_question_confirm_cancel":
        # Confirm cancellation
        await admin_confirm_cancel_question_flow(update, context)
    elif callback_data == "admin_question_continue":
        # Continue with current flow
        await admin_continue_question_flow(update, context)
    elif callback_data == "admin_question_save":
        # Save the question
        await admin_save_question(update, context)

# Move to Next Question Step
async def admin_move_to_next_question_step(update, context):
    """Move to the next step in question addition"""
    question_data = context.user_data.get('admin_question_data', {})
    current_step = question_data.get('step', 'question_text')
    
    # Define step flow
    steps = {
        'question_text': 'option_a',
        'option_a': 'option_b', 
        'option_b': 'option_c',
        'option_c': 'option_d',
        'option_d': 'option_e',
        'option_e': 'confirm'  # Final step
    }
    
    next_step = steps.get(current_step, 'confirm')
    question_data['step'] = next_step
    
    # Show appropriate prompt for next step
    if next_step == 'confirm':
        # Show confirmation screen
        course = question_data.get('course', 'Unknown')
        chapter = question_data.get('chapter', 'Unknown')
        chapter_display = chapter if chapter != "No Chapter" else "General"
        
        confirmation_text = (
            f"📝 Question for {course} - {chapter_display}:\n\n"
            f"❓ Question: {question_data.get('text', 'Not set')}\n\n"
            f"A) {question_data.get('option_a', 'Not set')}\n"
            f"B) {question_data.get('option_b', 'Not set')}\n"
            f"C) {question_data.get('option_c', 'Not set')}\n"
            f"D) {question_data.get('option_d', 'Not set')}\n"
        )
        
        if question_data.get('option_e'):
            confirmation_text += f"E) {question_data.get('option_e', 'Not set')}\n"
        
        confirmation_text += f"\nCorrect Answer: {question_data.get('correct_answer', 'A')}\n\nSave this question?"
        
        await safe_edit_message_text(update, 
            confirmation_text,
            reply_markup=get_admin_question_confirm_keyboard()
        )
    else:
        # Show next step prompt
        prompts = {
            'option_a': "Please send Option A:",
            'option_b': "Please send Option B:",
            'option_c': "Please send Option C:",
            'option_d': "Please send Option D:",
            'option_e': "Please send Option E (Optional):"
        }
        
        prompt = prompts.get(next_step, "Next step:")
        show_skip = next_step == 'option_e'
        
        await safe_edit_message_text(update, 
            prompt,
            reply_markup=get_admin_question_step_keyboard(next_step, show_skip)
        )

# Handle Question Text Input
async def admin_handle_question_text_input(update, context):
    """Handle text input during question addition"""
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.user_data.get('admin_question_flow'):
        return

    question_data = context.user_data.get('admin_question_data', {})
    current_step = question_data.get('step', 'question_text')
    
    text = update.message.text.strip()
    
    if current_step == 'question_text':
        question_data['text'] = text
    elif current_step == 'option_a':
        question_data['option_a'] = text
    elif current_step == 'option_b':
        question_data['option_b'] = text
    elif current_step == 'option_c':
        question_data['option_c'] = text
    elif current_step == 'option_d':
        question_data['option_d'] = text
    elif current_step == 'option_e':
        if text.lower() != 'skip':
            question_data['option_e'] = text
    
    # Move to next step
    await admin_move_to_next_question_step(update, context)

# Cancel Question Flow
async def admin_cancel_question_flow(update, context):
    """Cancel the question addition flow"""
    await safe_edit_message_text(update, 
        "❌ Cancel Question Addition\n\nAre you sure you want to cancel? All progress will be lost.",
        reply_markup=get_admin_question_cancel_keyboard()
    )

# Confirm Cancel Question Flow
async def admin_confirm_cancel_question_flow(update, context):
    """Confirm cancellation and clean up"""
    # Clear question flow data
    context.user_data.pop('admin_question_flow', None)
    context.user_data.pop('admin_question_data', None)
    context.user_data.pop('admin_question_course', None)
    context.user_data.pop('admin_question_chapter', None)
    
    await admin_questions_menu_enhanced(update, context)

# Continue Question Flow
async def admin_continue_question_flow(update, context):
    """Continue with the current question flow"""
    question_data = context.user_data.get('admin_question_data', {})
    current_step = question_data.get('step', 'question_text')
    
    # Show current step prompt
    prompts = {
        'question_text': "Please send the question text:",
        'option_a': "Please send Option A:",
        'option_b': "Please send Option B:",
        'option_c': "Please send Option C:",
        'option_d': "Please send Option D:",
        'option_e': "Please send Option E (Optional):"
    }
    
    prompt = prompts.get(current_step, "Continue:")
    show_skip = current_step == 'option_e'
    
    await safe_edit_message_text(update, 
        prompt,
        reply_markup=get_admin_question_step_keyboard(current_step, show_skip)
    )

# Save Question
async def admin_save_question(update, context):
    """Save the completed question to database"""
    question_data = context.user_data.get('admin_question_data', {})
    
    try:
        db = SessionLocal()
        
        # Create new question
        question = Question(
            text=question_data.get('text', ''),
            option_a=question_data.get('option_a', ''),
            option_b=question_data.get('option_b', ''),
            option_c=question_data.get('option_c', ''),
            option_d=question_data.get('option_d', ''),
            correct_answer=question_data.get('correct_answer', 'A'),
            course=question_data.get('course', ''),
            difficulty='medium',  # Default difficulty
            exam_id=1  # Default exam ID, should be configurable
        )
        
        # Add optional option E if provided
        if question_data.get('option_e'):
            # Store in option_c or create new field if needed
            question.option_c = question_data.get('option_e')
        
        db.add(question)
        db.commit()
        db.close()
        
        course = question_data.get('course', 'Unknown')
        chapter = question_data.get('chapter', 'Unknown')
        chapter_display = chapter if chapter != "No Chapter" else "General"
        
        await safe_edit_message_text(update, 
            f"✅ Question added successfully to {course} - {chapter_display}!",
            reply_markup=get_admin_questions_menu()
        )
        
        # Clear flow data
        context.user_data.pop('admin_question_flow', None)
        context.user_data.pop('admin_question_data', None)
        context.user_data.pop('admin_question_course', None)
        context.user_data.pop('admin_question_chapter', None)
        
    except Exception as e:
        await safe_edit_message_text(update, 
            f"❌ Error saving question: {str(e)}",
            reply_markup=get_admin_questions_menu()
        )

# Legacy handlers for compatibility
async def admin_add_question_enhanced(update, context):
    """Enhanced add question handler"""
    await admin_select_course_for_question(update, context)

async def admin_edit_question_start(update, context):
    """Edit question start handler"""
    await safe_edit_message_text(update, 
        "✏️ Edit Question\n\nQuestion editing functionality coming soon!",
        reply_markup=get_admin_questions_menu()
    )

async def admin_delete_question_start(update, context):
    """Delete question start handler"""
    await safe_edit_message_text(update, 
        "🗑️ Delete Question\n\nQuestion deletion functionality coming soon!",
        reply_markup=get_admin_questions_menu()
    )

# Back to main menu handler
async def admin_back_to_questions_menu(update, context):
    """Back to questions menu handler"""
    await admin_questions_menu_enhanced(update, context)
