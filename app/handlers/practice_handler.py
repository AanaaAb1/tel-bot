from app.database.session import SessionLocal
from app.models.user import User
from app.services.question_service import get_questions_by_course, get_questions_by_exam
from app.handlers.radio_question_handler import start_exam_with_polls
from app.keyboards.main_menu import main_menu
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

async def start_practice(update, context):
    """Start a practice session"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Check access
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    db.close()

    if not user or user.access != "UNLOCKED":
        await query.edit_message_text(
            "🔒 Access Locked\n\nPlease complete payment to unlock practice sessions.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Payment", callback_data="payment")]])
        )
        return

    # Show practice options
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Practice by Course", callback_data="practice_course")],
        [InlineKeyboardButton("📖 Practice by Chapter", callback_data="practice_chapter")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ])

    await query.edit_message_text(
        "🎯 Practice Mode\n\nChoose how you'd like to practice:",
        reply_markup=keyboard
    )

async def practice_by_course(update, context):
    """Show courses for practice"""
    query = update.callback_query
    await query.answer()

    from app.keyboards.course_keyboard import course_keyboard

    await query.edit_message_text(
        "Select a course to practice:",
        reply_markup=course_keyboard()
    )

async def practice_course_selected(update, context):
    """Start practice session for selected course"""
    query = update.callback_query
    await query.answer()

    course_id = int(query.data.replace("practice_course_", ""))

    # Get questions for this course
    questions = get_questions_by_course(course_id, limit=10)

    if not questions:
        await query.edit_message_text(
            "No questions available for this course yet.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="practice_course")]])
        )
        return

    # Initialize practice session
    context.user_data["user_id"] = query.from_user.id
    context.user_data["chat_id"] = query.message.chat_id
    context.user_data["questions"] = questions
    context.user_data["index"] = 0
    context.user_data["practice_mode"] = True
    context.user_data["use_timer"] = False  # Can be made configurable

    # Start practice with radio-style questions
    await start_exam_with_polls(update, context, context.user_data)

async def practice_by_chapter(update, context):
    """Show chapters (exams) for practice"""
    query = update.callback_query
    await query.answer()

    from app.keyboards.course_keyboard import course_keyboard

    await query.edit_message_text(
        "First select a course, then choose a chapter:",
        reply_markup=course_keyboard()
    )

async def practice_course_for_chapter(update, context):
    """Show chapters for selected course"""
    query = update.callback_query
    await query.answer()

    course_id = int(query.data.replace("practice_course_", ""))

    from app.keyboards.exam_keyboard import exam_selection_keyboard

    await query.edit_message_text(
        "Select a chapter to practice:",
        reply_markup=exam_selection_keyboard(course_id)
    )

async def practice_chapter_selected(update, context):
    """Start practice session for selected chapter (exam)"""
    query = update.callback_query
    await query.answer()

    exam_id = int(query.data.replace("practice_chapter_", ""))

    # Get questions for this exam
    questions = get_questions_by_exam(exam_id, limit=10)

    if not questions:
        await query.edit_message_text(
            "No questions available for this chapter yet.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="practice_chapter")]])
        )
        return

    # Initialize practice session
    context.user_data["user_id"] = query.from_user.id
    context.user_data["chat_id"] = query.message.chat_id
    context.user_data["questions"] = questions
    context.user_data["index"] = 0
    context.user_data["practice_mode"] = True
    context.user_data["use_timer"] = False

    # Start practice with radio-style questions
    await start_exam_with_polls(update, context, context.user_data)
