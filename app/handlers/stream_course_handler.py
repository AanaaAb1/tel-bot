"""
Stream-Specific Course Selection Handlers
Handle course selection for Natural Science and Social Science streams - ALL COURSES AVAILABLE TO BOTH STREAMS
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
    """Display Natural Science stream course selection - ALL COURSES AVAILABLE"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Check if user is admin (admins can access all courses)
    if user_id in ADMIN_IDS:
        # Show all courses to admin users
        courses = [
            ("📐 Mathematics", "maths"),
            ("📝 English", "english"),
            ("🧬 Biology", "bio"),
            ("⚛️ Physics", "physics"),
            ("⚗️ Chemistry", "chemistry"),
            ("📜 History", "history"),
            ("🌍 Geography", "geography"),
            ("🏛️ Government", "government"),
            ("💰 Economics", "economics"),
            ("📚 Literature", "literature")
        ]
        message = """
👑 Admin View: Natural Science Stream - ALL COURSES AVAILABLE

🎓 Complete Course Library for Natural Science Students:

Natural Science Subjects:
• Mathematics, English, Biology, Physics, Chemistry

Social Science Subjects:
• History, Geography, Government, Economics, Literature

All courses are now available to Natural Science stream students!
Select a course and chapter to start your exam:
        """
        
        # Create keyboard - now shows chapter selection
        keyboard = []
        for course_name, course_code in courses:
            keyboard.append([InlineKeyboardButton(
                course_name,
                callback_data=f"select_chapter_{course_code}"
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

    # ALL courses available for Natural Science stream (no level restrictions)
    courses = [
        ("📐 Mathematics", "maths"),
        ("📝 English", "english"),
        ("🧬 Biology", "bio"),
        ("⚛️ Physics", "physics"),
        ("⚗️ Chemistry", "chemistry"),
        ("📜 History", "history"),
        ("🌍 Geography", "geography"),
        ("🏛️ Government", "government"),
        ("💰 Economics", "economics"),
        ("📚 Literature", "literature")
    ]
    message = """
🧬 Natural Science Stream - ALL COURSES AVAILABLE

🎓 Complete Course Library for Natural Science Students:

Natural Science Subjects:
• Mathematics, English, Biology, Physics, Chemistry

Social Science Subjects:
• History, Geography, Government, Economics, Literature

All courses are now available to Natural Science stream students!
Select a course to start your exam:
    """

    # Create keyboard - now shows chapter selection
    keyboard = []
    for course_name, course_code in courses:
        keyboard.append([InlineKeyboardButton(
            course_name,
            callback_data=f"select_chapter_{course_code}"
        )])
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Dashboard", callback_data="natural_science_dashboard")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup
    )

async def select_social_science_course(update, context):
    """Display Social Science stream course selection - ALL COURSES AVAILABLE"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Check if user is admin (admins can access all courses)
    if user_id in ADMIN_IDS:
        # Show all courses to admin users
        courses = [
            ("📐 Mathematics", "maths"),
            ("📝 English", "english"),
            ("🧬 Biology", "bio"),
            ("⚛️ Physics", "physics"),
            ("⚗️ Chemistry", "chemistry"),
            ("📜 History", "history"),
            ("🌍 Geography", "geography"),
            ("🏛️ Government", "government"),
            ("💰 Economics", "economics"),
            ("📚 Literature", "literature")
        ]
        message = """
👑 Admin View: Social Science Stream - ALL COURSES AVAILABLE

🎓 Complete Course Library for Social Science Students:

Natural Science Subjects:
• Mathematics, English, Biology, Physics, Chemistry

Social Science Subjects:
• History, Geography, Government, Economics, Literature

All courses are now available to Social Science stream students!
Select a course and chapter to start your exam:
        """
        
        # Create keyboard - now shows chapter selection
        keyboard = []
        for course_name, course_code in courses:
            keyboard.append([InlineKeyboardButton(
                course_name,
                callback_data=f"select_chapter_{course_code}"
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

    # ALL courses available for Social Science stream (no level restrictions)
    courses = [
        ("📐 Mathematics", "maths"),
        ("📝 English", "english"),
        ("🧬 Biology", "bio"),
        ("⚛️ Physics", "physics"),
        ("⚗️ Chemistry", "chemistry"),
        ("📜 History", "history"),
        ("🌍 Geography", "geography"),
        ("🏛️ Government", "government"),
        ("💰 Economics", "economics"),
        ("📚 Literature", "literature")
    ]
    message = """
🌍 Social Science Stream - ALL COURSES AVAILABLE

🎓 Complete Course Library for Social Science Students:

Natural Science Subjects:
• Mathematics, English, Biology, Physics, Chemistry

Social Science Subjects:
• History, Geography, Government, Economics, Literature

All courses are now available to Social Science stream students!
Select a course to start your exam:
    """

    # Create keyboard - now shows chapter selection
    keyboard = []
    for course_name, course_code in courses:
        keyboard.append([InlineKeyboardButton(
            course_name,
            callback_data=f"select_chapter_{course_code}"
        )])
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Dashboard", callback_data="social_science_dashboard")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup
    )

async def handle_stream_course_selection(update, context):
    """Handle stream-specific course exam start - NO STREAM RESTRICTIONS"""
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

    # NO STREAM RESTRICTIONS - ALL COURSES AVAILABLE TO ALL STREAMS
    # Both Natural Science and Social Science students can access all courses
    
    # Start the exam
    await start_exam_selected(update, context)

async def handle_chapter_selection(update, context):
    """Handle chapter selection for courses"""
    query = update.callback_query
    await query.answer()

    course_code = query.data.replace("select_chapter_", "")
    
    # Course name mapping for display
    course_names = {
        "bio": "Biology",
        "physics": "Physics",
        "chemistry": "Chemistry", 
        "english": "English",
        "maths": "Mathematics",
        "geography": "Geography",
        "history": "History",
        "government": "Government",
        "economics": "Economics",
        "literature": "Literature"
    }
    
    course_name = course_names.get(course_code, course_code.title())
    
    # Check if this course exists in database
    from app.services.course_service import get_courses_by_code
    courses = get_courses_by_code(course_code)
    
    if not courses:
        # Course doesn't exist in database - show error message
        missing_courses = ['geography', 'history', 'government', 'economics', 'literature']
        if course_code.lower() in missing_courses:
            await query.edit_message_text(
                f"⚠️ Course Unavailable\n\n"
                f"The course '{course_name}' is not available in our exam system yet.\n\n"
                f"📚 Currently Available Courses:\n"
                f"• Mathematics\n"
                f"• Physics\n" 
                f"• Chemistry\n"
                f"• Biology\n"
                f"• English\n\n"
                f"Please select from the available courses above.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("↩️ Back to Natural Science", callback_data="select_ns_course")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
                ])
            )
        else:
            await query.edit_message_text(
                "Course not found.\n\nPlease try selecting from the available courses.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("↩️ Back to Natural Science", callback_data="select_ns_course")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
                ])
            )
        return
    
    # Show chapter selection
    try:
        from app.keyboards.chapter_selection_keyboard import get_chapter_selection_keyboard, get_chapter_selection_message
        
        keyboard = get_chapter_selection_keyboard(course_name, course_code)
        message = get_chapter_selection_message(course_name, course_code)
        
        await query.edit_message_text(
            text=message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except ImportError:
        # Chapter selection keyboard doesn't exist, show simple message
        await query.edit_message_text(
            f"📚 {course_name} Course Selected\n\n"
            f"This course is available for exams. Chapters will be added soon!\n\n"
            f"Please check back later for chapter selection.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("↩️ Back to Natural Science", callback_data="select_ns_course")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
            ])
        )

async def handle_chapter_exam_start(update, context):
    """Handle exam start with chapter specification"""
    query = update.callback_query
    await query.answer()

    # Parse chapter exam callback data
    # Format: start_chapter_exam_{course_code}_{chapter}
    data_parts = query.data.split("_")
    if len(data_parts) >= 4:
        course_code = data_parts[3]  # start_chapter_exam_coursecode_chapter
        chapter = data_parts[4]
        
        # Store chapter info in context
        context.user_data['chapter'] = chapter
        
        # Start the exam with chapter context
        await start_exam_selected(update, context)
    else:
        await query.edit_message_text("❌ Invalid chapter selection. Please try again.")

def register_stream_course_handlers(application):
    """Register stream-specific course handlers"""
    application.add_handler(CallbackQueryHandler(
        select_natural_science_course, 
        pattern="^select_ns_course$"
    ))
    application.add_handler(CallbackQueryHandler(
        select_social_science_course, 
        pattern="^select_ss_course$"
    ))
    application.add_handler(CallbackQueryHandler(
        handle_chapter_selection, 
        pattern="^select_chapter_"
    ))
    application.add_handler(CallbackQueryHandler(
        handle_chapter_exam_start, 
        pattern="^start_chapter_exam_"
    ))
