"""
Stream-Specific Dashboard Handlers
Separate dashboards for Natural Science and Social Science streams
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.session import SessionLocal
from app.models.user import User
from app.handlers.materials_handler import materials_menu
from app.handlers.practice_handler import start_practice
from app.handlers.leaderboard_handler import show_leaderboard
from app.handlers.profile_handler_fixed import profile_menu
from app.handlers.result_handler import user_result_history
from app.keyboards.stream_menu_keyboard import (
    get_natural_science_dashboard_keyboard, 
    get_social_science_dashboard_keyboard,
    get_natural_science_dashboard_message,
    get_social_science_dashboard_message
)
from app.utils.access_control import check_level_access
from app.config.constants import ADMIN_IDS
from telegram.error import BadRequest

async def natural_science_dashboard(update, context):
    """Display Natural Science Stream Dashboard"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Check if user is admin (admins can access all dashboards)
    if user_id in ADMIN_IDS:
        # For admin users, create a mock user object for the dashboard
        from types import SimpleNamespace
        user = SimpleNamespace(
            name="Admin User",
            stream="natural_science",  # Set stream for display purposes
            level="admin",
            access="UNLOCKED"
        )
        message = f"👑 Admin View: Natural Science Dashboard\n\nWelcome back, Admin! You have full access to all features."
        keyboard = get_natural_science_dashboard_keyboard(user_id)
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard
        )
        return

    # Get user information
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    db.close()

    if not user:
        await query.edit_message_text("❌ User information not found. Please register again.")
        return

    # Verify user has Natural Science stream access
    if user.stream != "natural_science":
        await query.edit_message_text("❌ Access denied. This dashboard is for Natural Science stream users only.")
        return

    # Check if user has access (payment and level validation)
    if user.access == "LOCKED":
        from app.keyboards.payment_keyboard import payment_keyboard
        await query.edit_message_text(
            "⚠️ Access Restricted\n\n"
            "You must complete payment to access Natural Science stream features.\n\n"
            "Please proceed to payment and wait for admin approval.",
            reply_markup=payment_keyboard()
        )
        return

    # Display Natural Science dashboard
    message = get_natural_science_dashboard_message(user)
    keyboard = get_natural_science_dashboard_keyboard(user_id)

    await query.edit_message_text(
        message,
        reply_markup=keyboard
    )

async def social_science_dashboard(update, context):
    """Display Social Science Stream Dashboard"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Check if user is admin (admins can access all dashboards)
    if user_id in ADMIN_IDS:
        # For admin users, create a mock user object for the dashboard
        from types import SimpleNamespace
        user = SimpleNamespace(
            name="Admin User",
            stream="social_science",  # Set stream for display purposes
            level="admin",
            access="UNLOCKED"
        )
        message = f"👑 Admin View: Social Science Dashboard\n\nWelcome back, Admin! You have full access to all features."
        keyboard = get_social_science_dashboard_keyboard(user_id)
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard
        )
        return

    # Get user information
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    db.close()

    if not user:
        await query.edit_message_text("❌ User information not found. Please register again.")
        return

    # Verify user has Social Science stream access
    if user.stream != "social_science":
        await query.edit_message_text("❌ Access denied. This dashboard is for Social Science stream users only.")
        return

    # Check if user has access (payment and level validation)
    if user.access == "LOCKED":
        from app.keyboards.payment_keyboard import payment_keyboard
        await query.edit_message_text(
            "⚠️ Access Restricted\n\n"
            "You must complete payment to access Social Science stream features.\n\n"
            "Please proceed to payment and wait for admin approval.",
            reply_markup=payment_keyboard()
        )
        return

    # Display Social Science dashboard
    message = get_social_science_dashboard_message(user)
    keyboard = get_social_science_dashboard_keyboard(user_id)

    await query.edit_message_text(
        message,
        reply_markup=keyboard
    )

async def handle_natural_science_action(update, context):
    """Handle Natural Science stream-specific actions"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action = query.data

    # Verify user has Natural Science stream access
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    db.close()

    if not user or user.stream != "natural_science":
        await query.edit_message_text("❌ Access denied.")
        return

    # Handle different actions
    if action == "ns_profile":
        await profile_menu(update, context)
    elif action == "ns_practice":
        await start_practice(update, context)
    elif action == "ns_leaderboard":
        await show_leaderboard(update, context)
    elif action == "ns_materials":
        await materials_menu(update, context)
    elif action == "ns_results":
        await user_result_history(update, context)
    elif action == "ns_back_to_main":
        from app.keyboards.main_menu import main_menu
        try:
            await query.edit_message_text(
                "Choose an option:",
                reply_markup=main_menu(user_id)
            )
        except BadRequest:
            await query.answer("Menu updated")
    else:
        await query.edit_message_text("❌ Action not found.")

async def handle_social_science_action(update, context):
    """Handle Social Science stream-specific actions"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action = query.data

    # Verify user has Social Science stream access
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    db.close()

    if not user or user.stream != "social_science":
        await query.edit_message_text("❌ Access denied.")
        return

    # Handle different actions
    if action == "ss_profile":
        await profile_menu(update, context)
    elif action == "ss_practice":
        await start_practice(update, context)
    elif action == "ss_leaderboard":
        await show_leaderboard(update, context)
    elif action == "ss_materials":
        await materials_menu(update, context)
    elif action == "ss_results":
        await user_result_history(update, context)
    elif action == "ss_back_to_main":
        from app.keyboards.main_menu import main_menu
        try:
            await query.edit_message_text(
                "Choose an option:",
                reply_markup=main_menu(user_id)
            )
        except BadRequest:
            await query.answer("Menu updated")
    else:
        await query.edit_message_text("❌ Action not found.")

async def natural_science_exams(update, context):
    """Display Natural Science stream exams"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Verify user has Natural Science stream access
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    db.close()

    if not user or user.stream != "natural_science":
        await query.edit_message_text("❌ Access denied. This section is for Natural Science stream users only.")
        return

    # Redirect to stream-specific course selection
    from app.handlers.stream_course_handler import select_natural_science_course
    await select_natural_science_course(update, context)

async def social_science_exams(update, context):
    """Display Social Science stream exams"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Verify user has Social Science stream access
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    db.close()

    if not user or user.stream != "social_science":
        await query.edit_message_text("❌ Access denied. This section is for Social Science stream users only.")
        return

    # Redirect to stream-specific course selection
    from app.handlers.stream_course_handler import select_social_science_course
    await select_social_science_course(update, context)
