from app.database.session import SessionLocal
from app.models.user import User
from app.models.course import Course
from app.models.chapter import Chapter
from app.services.course_service import get_course_by_id, get_course_by_name
from app.services.chapter_service import get_chapters_by_course
from app.services.question_service import get_questions_by_chapter
from app.keyboards.main_menu import main_menu
from app.handlers.radio_question_handler import start_exam_with_polls
from app.keyboards.payment_keyboard import payment_keyboard
from app.keyboards.admin_question_keyboard import get_admin_course_selection_keyboard
from app.config.constants import ADMIN_IDS
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

async def select_course(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    
    # CRITICAL: Admins ALWAYS skip payment checks and get immediate access
    if user_id in ADMIN_IDS:
        # Admin gets immediate access - no payment required!
        pass
    else:
        # Check payment status for regular users only
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=user_id).first()
        db.close()

        if not user or user.access == "LOCKED":
            await query.edit_message_text(
                "⚠️ Access Restricted\n\n"
                "You must complete payment to access exams.\n\n"
                "Please proceed to payment and wait for admin approval.",
                reply_markup=payment_keyboard()
            )
            return

    course_id = int(query.data.replace("exam_course_", ""))

    course = get_course_by_id(course_id)
    if not course:
        await query.edit_message_text("Course not found.")
        return

    # Get chapters for this course
    chapters = get_chapters_by_course(course_id)

    # Build course content message
    message = f"📚 {course.name}\n\n"
    if course.description:
        message += f"{course.description}\n\n"

    message += "📖 chapter:\n"
    keyboard_buttons = []
    if chapters:
        for i, chapter in enumerate(chapters, 1):
            message += f"{i}. {chapter.name}\n"
            keyboard_buttons.append([InlineKeyboardButton(f"📝 Take {chapter.name}", callback_data=f"start_exam_{chapter.id}")])
    else:
        message += "No chapters available yet.\n"

    # Add Add Question button for admins (only show if user is admin)
    if user_id in ADMIN_IDS:
        keyboard_buttons.append([InlineKeyboardButton("➕ Add Question", callback_data=f"admin_add_question_{course.id}_{course.name}")])

    # Add back button
    keyboard_buttons.append([InlineKeyboardButton("⬅️ Back to Courses", callback_data="courses")])
    keyboard_buttons.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await query.edit_message_text(message, reply_markup=keyboard)

async def start_exam_selected(update, context):
    """Start exam for selected chapter"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    chapter_id = int(query.data.replace("start_exam_", ""))

    # CRITICAL: Admins ALWAYS skip payment checks
    if user_id not in ADMIN_IDS:
        # Check payment status for regular users only
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        db.close()

        if not user or user.access == "LOCKED":
            await query.edit_message_text(
                "⚠️ Access Restricted\n\n"
                "You must complete payment to access exams.\n\n"
                "Please proceed to payment and wait for admin approval.",
                reply_markup=payment_keyboard()
            )
            return

    # Get questions for this chapter
    questions = get_questions_by_chapter(chapter_id, limit=None)  # Get all questions for chapter

    if not questions:
        await query.edit_message_text(
            "No questions available for this chapter yet.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="courses")]])
        )
        return

    # Initialize exam session
    context.user_data["user_id"] = query.from_user.id
    context.user_data["chat_id"] = query.message.chat_id
    context.user_data["chapter_id"] = chapter_id
    context.user_data["questions"] = questions
    context.user_data["index"] = 0
    context.user_data["use_timer"] = False  # Can be made configurable

    # Start exam with radio-style questions
    await start_exam_with_polls(update, context, context.user_data)
