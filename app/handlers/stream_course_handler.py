"""
Stream-Specific Course Selection Handlers
Handle course selection for Natural Science and Social Science streams
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
from app.database.session import SessionLocal
from app.models.user import User
from app.handlers.course_handler import start_exam_selected
from app.handlers.exam_handler import start_exam
from app.config.constants import ADMIN_IDS
from telegram.error import BadRequest

def get_stream_course_handler():
    """Return handler for stream-specific course selection"""
    return CallbackQueryHandler(handle_stream_course_selection, pattern="^select_(ns|ss)_course$")

async def select_natural_science_course(update, context):
    """Display Natural Science stream course selection"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Check if user is admin (admins can access all courses)
    if user_id in ADMIN_IDS:
        # Show all Natural Science courses to admin users
        courses = [
            ("📐 Mathematics", "maths"),
            ("📝 English", "english"),
            ("🧬 Biology", "bio"),
            ("⚛️ Physics", "physics"),
            ("⚗️ Chemistry", "chemistry")
        ]
        message = """
👑 Admin View: Natural Science Stream Courses

🎓 All Available Courses for Natural Science Stream:

• Mathematics, English
• Biology, Physics, Chemistry

Select a course to start your exam:
        """
        
        # Create keyboard
        keyboard = []
        for course_name, course_code in courses:
            keyboard.append([InlineKeyboardButton(
                course_name,
                callback_data=f"start_exam_{course_code}"
            )])
        
        keyboard.append([InlineKeyboardButton("↩️ Back to Dashboard", callback_data="natural_science_dashboard")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup
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
        await query.edit_message_text("❌ Access denied. This section is for Natural Science stream users only.")
        return

    # Check access
    if user.access == "LOCKED":
        from app.keyboards.payment_keyboard import payment_keyboard
        await query.edit_message_text(
            "⚠️ Access Restricted\n\n"
            "You must complete payment to access Natural Science stream exams.\n\n"
            "Please proceed to payment and wait for admin approval.",
            reply_markup=payment_keyboard()
        )
        return

    # Define Natural Science courses based on user level
    if user.level and user.level.lower() == "remedial":
        # Remedial Natural Science students get basic science courses
        courses = [
            ("📐 Mathematics", "maths"),
            ("📝 English", "english"),
            ("🧬 Biology", "bio"),
            ("⚛️ Physics", "physics"),
            ("⚗️ Chemistry", "chemistry")
        ]
        message = """
🧬 Natural Science Stream - Remedial Level

🔰 Available Courses for Remedial Students:

Common Subjects:
• Mathematics, English

Science Subjects:
• Biology, Physics, Chemistry

Select a course to start your exam:
        """
    elif user.level and user.level.lower() == "freshman":
        # Freshman Natural Science students get all available courses
        courses = [
            ("📐 Mathematics", "maths"),
            ("📝 English", "english"),
            ("🧬 Biology", "bio"),
            ("⚛️ Physics", "physics"),
            ("⚗️ Chemistry", "chemistry")
        ]
        message = """
🧬 Natural Science Stream - Freshman Level

🎓 Available Courses for Freshman Students:

All Natural Science Subjects:
• Mathematics, English
• Biology, Physics, Chemistry

Select a course to start your exam:
        """
    else:
        # Default to basic courses
        courses = [
            ("📐 Mathematics", "maths"),
            ("📝 English", "english")
        ]
        message = """
🧬 Natural Science Stream Courses

📚 Available Courses:

Basic Subjects:
• Mathematics, English

Select a course to start your exam:
        """

    # Create keyboard
    keyboard = []
    for course_name, course_code in courses:
        keyboard.append([InlineKeyboardButton(
            course_name,
            callback_data=f"start_exam_{course_code}"
        )])
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Dashboard", callback_data="natural_science_dashboard")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup
    )

async def select_social_science_course(update, context):
    """Display Social Science stream course selection"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Check if user is admin (admins can access all courses)
    if user_id in ADMIN_IDS:
        # Show all Social Science courses to admin users
        courses = [
            ("📐 Mathematics", "maths"),
            ("📝 English", "english"),
            ("📜 History", "history"),
            ("🌍 Geography", "geography"),
            ("🏛️ Government", "government"),
            ("💰 Economics", "economics"),
            ("📚 Literature", "literature")
        ]
        message = """
👑 Admin View: Social Science Stream Courses

🎓 All Available Courses for Social Science Stream:

• Mathematics, English
• History, Geography, Government
• Economics, Literature

Select a course to start your exam:
        """
        
        # Create keyboard
        keyboard = []
        for course_name, course_code in courses:
            keyboard.append([InlineKeyboardButton(
                course_name,
                callback_data=f"start_exam_{course_code}"
            )])
        
        keyboard.append([InlineKeyboardButton("↩️ Back to Dashboard", callback_data="social_science_dashboard")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup
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
        await query.edit_message_text("❌ Access denied. This section is for Social Science stream users only.")
        return

    # Check access
    if user.access == "LOCKED":
        from app.keyboards.payment_keyboard import payment_keyboard
        await query.edit_message_text(
            "⚠️ Access Restricted\n\n"
            "You must complete payment to access Social Science stream exams.\n\n"
            "Please proceed to payment and wait for admin approval.",
            reply_markup=payment_keyboard()
        )
        return

    # Define Social Science courses based on user level
    if user.level and user.level.lower() == "remedial":
        # Remedial Social Science students get basic social studies courses
        courses = [
            ("📐 Mathematics", "maths"),
            ("📝 English", "english"),
            ("📜 History", "history"),
            ("🌍 Geography", "geography")
        ]
        message = """
🌍 Social Science Stream - Remedial Level

🔰 Available Courses for Remedial Students:

Common Subjects:
• Mathematics, English

Social Studies:
• History, Geography

Select a course to start your exam:
        """
    elif user.level and user.level.lower() == "freshman":
        # Freshman Social Science students get all available courses
        courses = [
            ("📐 Mathematics", "maths"),
            ("📝 English", "english"),
            ("📜 History", "history"),
            ("🌍 Geography", "geography"),
            ("🏛️ Government", "government"),
            ("💰 Economics", "economics"),
            ("📚 Literature", "literature")
        ]
        message = """
🌍 Social Science Stream - Freshman Level

🎓 Available Courses for Freshman Students:

All Social Science Subjects:
• Mathematics, English
• History, Geography, Government
• Economics, Literature

Select a course to start your exam:
        """
    else:
        # Default to basic courses
        courses = [
            ("📐 Mathematics", "maths"),
            ("📝 English", "english")
        ]
        message = """
🌍 Social Science Stream Courses

📚 Available Courses:

Basic Subjects:
• Mathematics, English

Select a course to start your exam:
        """

    # Create keyboard
    keyboard = []
    for course_name, course_code in courses:
        keyboard.append([InlineKeyboardButton(
            course_name,
            callback_data=f"start_exam_{course_code}"
        )])
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Dashboard", callback_data="social_science_dashboard")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup
    )

async def handle_stream_course_selection(update, context):
    """Handle stream-specific course exam start"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    course_code = query.data.replace("start_exam_", "")

    # Get user information
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    db.close()

    if not user:
        await query.edit_message_text("❌ User information not found. Please register again.")
        return

    # Verify user has appropriate stream access for the course
    natural_science_courses = ["maths", "english", "bio", "physics", "chemistry"]
    social_science_courses = ["maths", "english", "history", "geography", "government", "economics", "literature"]

    if user.stream == "natural_science" and course_code not in natural_science_courses:
        await query.edit_message_text("❌ Access denied. This course is not available in your Natural Science stream.")
        return
    elif user.stream == "social_science" and course_code not in social_science_courses:
        await query.edit_message_text("❌ Access denied. This course is not available in your Social Science stream.")
        return

    # Start the exam
    await start_exam_selected(update, context)
