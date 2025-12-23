from app.database.session import SessionLocal
from app.models.user import User
from app.services.course_service import get_course_by_id
from app.services.exam_service import get_exams_by_course
from app.services.question_service import get_questions_by_exam
from app.keyboards.main_menu import main_menu
from app.handlers.radio_question_handler import start_exam_with_polls
from app.keyboards.payment_keyboard import payment_keyboard
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

async def select_course(update, context):
    query = update.callback_query
    await query.answer()

    # Double-check access status for security
    user_id = query.from_user.id
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

    # Get exams for this course (as chapters)
    exams = get_exams_by_course(course_id)

    # Build course content message
    message = f"📚 {course.name}\n\n"
    if course.description:
        message += f"{course.description}\n\n"

    message += "📖 Chapters:\n"
    keyboard_buttons = []
    if exams:
        for i, exam in enumerate(exams, 1):
            message += f"{i}. {exam.name}\n"
            keyboard_buttons.append([InlineKeyboardButton(f"📝 Take {exam.name}", callback_data=f"start_exam_{exam.id}")])
    else:
        message += "No chapters available yet.\n"

    # Add back button
    keyboard_buttons.append([InlineKeyboardButton("⬅️ Back to Courses", callback_data="courses")])
    keyboard_buttons.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await query.edit_message_text(message, reply_markup=keyboard)

async def start_exam_selected(update, context):
    """Start exam for selected chapter"""
    query = update.callback_query
    await query.answer()

    exam_id = int(query.data.replace("start_exam_", ""))

    # Get questions for this exam
    questions = get_questions_by_exam(exam_id, limit=None)  # Get all questions for exam

    if not questions:
        await query.edit_message_text(
            "No questions available for this exam yet.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="courses")]])
        )
        return

    # Check if user has access (payment status)
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

    # Initialize exam session
    context.user_data["user_id"] = query.from_user.id
    context.user_data["chat_id"] = query.message.chat_id
    context.user_data["exam_id"] = exam_id
    context.user_data["questions"] = questions
    context.user_data["index"] = 0
    context.user_data["use_timer"] = False  # Can be made configurable

    # Start exam with radio-style questions
    await start_exam_with_polls(update, context, context.user_data)

