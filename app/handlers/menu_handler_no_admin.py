from app.handlers.exam_handler import start_exam
from app.handlers.payment_handler import payment_menu
from app.handlers.result_handler import user_result_history
from app.handlers.practice_handler import start_practice
from app.handlers.materials_handler import materials_menu
from app.handlers.leaderboard_handler import show_leaderboard, show_leaderboard_best, show_leaderboard_latest, show_leaderboard_average
from app.handlers.profile_handler_fixed import profile_menu
from app.handlers.course_handler import select_course, start_exam_selected
from app.keyboards.main_menu_no_admin import main_menu
from app.database.session import SessionLocal
from app.models.user import User
from telegram.error import BadRequest

async def menu(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Check access for protected sections - CRITICAL SECURITY FIX
    # Include course and exam patterns to prevent bypass
    if (query.data in ["courses", "exams", "materials", "practice", "leaderboard"] or 
        query.data.startswith("exam_course_") or query.data.startswith("start_exam_")):
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=user_id).first()
        db.close()

        if user and user.access == "LOCKED":
            from app.keyboards.payment_keyboard import payment_keyboard
            await query.edit_message_text(
                "⚠️ Access Restricted\n\n"
                "You must complete payment to access exams.\n\n"
                "Please proceed to payment and wait for admin approval.",
                reply_markup=payment_keyboard()
            )
            return

    # Handle course and exam patterns with access control
    if query.data.startswith("exam_course_"):
        await select_course(update, context)
    elif query.data.startswith("start_exam_"):
        await start_exam_selected(update, context)
    elif query.data == "profile":
        await profile_menu(update, context)
    elif query.data == "exams":
        await start_exam(update, context)
    elif query.data == "payment":
        await payment_menu(update, context)
    elif query.data == "materials":
        await materials_menu(update, context)
    elif query.data == "courses":
        # Show courses (assuming course selection)
        from app.keyboards.course_keyboard import course_keyboard
        await query.edit_message_text(
            "Select a course:",
            reply_markup=course_keyboard()
        )
    elif query.data == "practice":
        await start_practice(update, context)
    elif query.data == "leaderboard":
        await show_leaderboard(update, context)
    elif query.data == "leaderboard_best":
        await show_leaderboard_best(update, context)
    elif query.data == "leaderboard_latest":
        await show_leaderboard_latest(update, context)
    elif query.data == "leaderboard_average":
        await show_leaderboard_average(update, context)
    elif query.data == "back_to_main":
        try:
            await query.edit_message_text(
                "Choose an option:",
                reply_markup=main_menu(user_id)
            )
        except BadRequest:
            await query.answer("Menu updated")
    elif query.data == "help":
        try:
            await query.edit_message_text(
                "Help: Contact admin for support.",
                reply_markup=main_menu(user_id)
            )
        except BadRequest:
            await query.answer("Help section updated")
    else:
        try:
            await query.edit_message_text(
                "Choose an option:",
                reply_markup=main_menu(user_id)
            )
        except BadRequest:
            await query.answer("Menu refreshed")
