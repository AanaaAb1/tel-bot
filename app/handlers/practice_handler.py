from app.database.session import SessionLocal
from app.models.user import User
from app.services.question_service import get_questions_by_course, get_questions_by_exam
from app.handlers.radio_question_handler_poll import show_question_as_poll
from app.keyboards.main_menu import main_menu
from app.config.constants import ACCESS_UNLOCKED
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

    if not user or user.access != ACCESS_UNLOCKED:
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
    """Start practice session for selected course with enhanced question retrieval"""
    query = update.callback_query
    await query.answer()

    course_id = int(query.data.replace("practice_course_", ""))

    # Enhanced question retrieval using course/chapter organization
    from app.services.question_service import get_questions_by_course_name
    from app.models.course import Course
    
    db = SessionLocal()
    try:
        # Get course info
        course = db.query(Course).filter_by(id=course_id).first()
        if not course:
            await query.edit_message_text(
                "Course not found.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="practice_course")]])
            )
            return

        # Get questions for this course using enhanced method
        questions = get_questions_by_course_name(course.name, limit=10)

    finally:
        db.close()

    if not questions:
        await query.edit_message_text(
            f"📚 No questions available yet for {course.name}.\n\n"
            f"Ask an admin to add questions for this course.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Question", callback_data=f"admin_add_question_{course.id}_{course.name}")],
                [InlineKeyboardButton("⬅️ Back", callback_data="practice_course")]
            ])
        )
        return

    # Initialize practice session
    context.user_data["user_id"] = query.from_user.id
    context.user_data["chat_id"] = query.message.chat_id
    context.user_data["questions"] = questions
    context.user_data["index"] = 0
    context.user_data["practice_mode"] = True
    context.user_data["use_timer"] = False  # Can be made configurable
    context.user_data["course_name"] = course.name
    context.user_data["chapter_completion"] = True  # Enable chapter completion tracking

    # Start practice with radio-style poll questions
    await show_question_as_poll(update, context, context.user_data)

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

    course_id = int(query.data.replace("practice_course_chapter_", ""))

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
    context.user_data["chapter_completion"] = True  # Enable chapter completion tracking

    # Start practice with radio-style poll questions
    await show_question_as_poll(update, context, context.user_data)
