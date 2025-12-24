from app.handlers.exam_handler import start_exam
from app.handlers.payment_handler import payment_menu
from app.handlers.result_handler import user_result_history
from app.handlers.admin_handler import admin_payments, exam_analytics, admin_panel
from app.handlers.practice_handler import start_practice
from app.handlers.materials_handler import materials_menu
from app.handlers.leaderboard_handler import show_leaderboard, show_leaderboard_best, show_leaderboard_latest, show_leaderboard_average
from app.handlers.profile_handler_fixed import profile_menu
from app.handlers.course_handler import select_course, start_exam_selected
from app.handlers.stream_dashboard_handler import (
    natural_science_dashboard, 
    social_science_dashboard,
    handle_natural_science_action,
    handle_social_science_action,
    natural_science_exams,
    social_science_exams
)
from app.keyboards.main_menu import main_menu
from app.config.constants import ADMIN_IDS
from app.database.session import SessionLocal
from app.models.user import User
from app.utils.access_control import check_level_access, get_user_accessible_levels
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
    elif query.data == "courses":
        # Route to stream-specific dashboard based on user's stream
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=user_id).first()
        db.close()
        
        if user and user.stream:
            if user.stream == "natural_science":
                await natural_science_dashboard(update, context)
            elif user.stream == "social_science":
                await social_science_dashboard(update, context)
            else:
                await query.edit_message_text(
                    "❌ Stream information not found. Please register again to select your stream."
                )
        else:
            await query.edit_message_text(
                "❌ Stream information not found. Please register again to select your stream."
            )
    elif query.data == "exams":
        # Show stream-specific course selection
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=user_id).first()
        db.close()
        
        if user and user.stream:
            from app.keyboards.stream_course_keyboard import get_stream_courses_keyboard, get_stream_courses_message
            
            courses_message = get_stream_courses_message(user.stream, user_id)
            courses_keyboard = get_stream_courses_keyboard(user.stream, user_id)
            
            await query.edit_message_text(
                courses_message,
                reply_markup=courses_keyboard
            )
        else:
            await query.edit_message_text(
                "❌ Stream information not found. Please register again to select your stream."
            )
    elif query.data == "natural_science_dashboard":
        await natural_science_dashboard(update, context)
    elif query.data == "social_science_dashboard":
        await social_science_dashboard(update, context)
    elif query.data.startswith("ns_"):
        await handle_natural_science_action(update, context)
    elif query.data.startswith("ss_"):
        await handle_social_science_action(update, context)
    elif query.data == "ns_exams":
        await natural_science_exams(update, context)
    elif query.data == "ss_exams":
        await social_science_exams(update, context)
    elif query.data == "payment":
        await payment_menu(update, context)
    elif query.data == "materials":
        await materials_menu(update, context)
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
    elif query.data == "admin":
        if user_id in ADMIN_IDS:
            await admin_panel(update, context)
        else:
            try:
                await query.edit_message_text("Access denied.")
            except BadRequest:
                await query.answer("Access denied.")
    elif query.data == "analytics":
        if user_id in ADMIN_IDS:
            await exam_analytics(update, context)
        else:
            try:
                await query.edit_message_text("Access denied.")
            except BadRequest:
                await query.answer("Access denied.")
    elif query.data == "admin_payments":
        if user_id in ADMIN_IDS:
            await admin_payments(update, context)
        else:
            try:
                await query.edit_message_text("Access denied.")
            except BadRequest:
                await query.answer("Access denied.")
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
