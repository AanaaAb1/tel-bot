"""
Stream-Specific Course Handler
Handles course selection from stream-specific keyboards
"""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, ConversationHandler
from app.models.user import User
from app.keyboards.course_menu_keyboard import get_course_menu_keyboard, get_course_menu_message
from app.utils.access_control import check_course_access

# Course state
BIOLOGY, PHYSICS, CHEMISTRY, MATHEMATICS, ENGLISH, GEOGRAPHY, HISTORY = range(7)

async def stream_course_callback(update: Update, context: CallbackContext):
    """Handle stream course button clicks"""
    query = update.callback_query
    await query.answer()
    
    # Get user from database
    user = User.get_by_telegram_id(update.effective_user.id)
    if not user:
        await query.edit_message_text("❌ User not found. Please register first.")
        return ConversationHandler.END
    
    # Extract course from callback data
    callback_data = query.data
    if not callback_data.startswith("stream_course_"):
        await query.edit_message_text("❌ Invalid course selection.")
        return ConversationHandler.END
    
    course_code = callback_data.replace("stream_course_", "")
    
    # Map course codes to course names and states
    course_mapping = {
        "bio": ("Biology", BIOLOGY),
        "physics": ("Physics", PHYSICS),
        "chemistry": ("Chemistry", CHEMISTRY),
        "maths": ("Mathematics", MATHEMATICS),
        "english": ("English", ENGLISH),
        "geography": ("Geography", GEOGRAPHY),
        "history": ("History", HISTORY)
    }
    
    if course_code not in course_mapping:
        await query.edit_message_text("❌ Course not found.")
        return ConversationHandler.END
    
    course_name, course_state = course_mapping[course_code]
    
    # Validate course access based on user's stream
    if not check_course_access(user, course_name):
        stream_name = user.stream.replace("_", " ").title() if user.stream else "Unknown"
        await query.edit_message_text(
            f"❌ **{course_name}** is not available for {stream_name} stream.\n\n"
            f"Please select a course available in your stream.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # Store selected course in user context
    context.user_data['selected_course'] = course_name
    context.user_data['course_state'] = course_state
    
    # Show course menu
    course_menu_message = get_course_menu_message(course_name)
    course_menu_keyboard = get_course_menu_keyboard()
    
    await query.edit_message_text(
        course_menu_message,
        reply_markup=course_menu_keyboard,
        parse_mode='Markdown'
    )
    
    return course_state

async def handle_course_menu_callback(update: Update, context: CallbackContext):
    """Handle course menu button clicks"""
    query = update.callback_query
    await query.answer()
    
    selected_course = context.user_data.get('selected_course')
    if not selected_course:
        await query.edit_message_text("❌ No course selected. Please select a course first.")
        return ConversationHandler.END
    
    callback_data = query.data
    
    # Handle different course menu actions
    if callback_data == "back_to_courses":
        # Return to course selection
        from app.keyboards.stream_course_keyboard import get_stream_courses_keyboard, get_stream_courses_message
        
        user = User.get_by_telegram_id(update.effective_user.id)
        if user and user.stream:
            user_id = update.effective_user.id
            courses_message = get_stream_courses_message(user.stream, user_id)
            courses_keyboard = get_stream_courses_keyboard(user.stream, user_id)
            
            await query.edit_message_text(
                courses_message,
                reply_markup=courses_keyboard,
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        else:
            await query.edit_message_text("❌ Stream information not found.")
            return ConversationHandler.END
    
    elif callback_data.startswith("exam_"):
        # Handle exam selection for the course
        await query.edit_message_text(
            f"📝 **{selected_course} Exams**\n\n"
            f"Exam functionality for {selected_course} will be available soon!",
            parse_mode='Markdown'
        )
        return context.user_data.get('course_state', BIOLOGY)
    
    elif callback_data.startswith("practice_"):
        # Handle practice selection for the course
        await query.edit_message_text(
            f"🎯 **{selected_course} Practice**\n\n"
            f"Practice sessions for {selected_course} will be available soon!",
            parse_mode='Markdown'
        )
        return context.user_data.get('course_state', BIOLOGY)
    
    elif callback_data.startswith("materials_"):
        # Handle materials selection for the course
        await query.edit_message_text(
            f"📚 **{selected_course} Materials**\n\n"
            f"Study materials for {selected_course} will be available soon!",
            parse_mode='Markdown'
        )
        return context.user_data.get('course_state', BIOLOGY)
    
    elif callback_data.startswith("analytics_"):
        # Handle analytics for the course
        await query.edit_message_text(
            f"📊 **{selected_course} Analytics**\n\n"
            f"Performance analytics for {selected_course} will be available soon!",
            parse_mode='Markdown'
        )
        return context.user_data.get('course_state', BIOLOGY)
    
    else:
        await query.edit_message_text("❌ Invalid menu option selected.")
        return context.user_data.get('course_state', BIOLOGY)

def get_stream_course_handler():
    """Get the stream course conversation handler"""
    from app.keyboards.stream_course_keyboard import get_stream_courses_keyboard, get_stream_courses_message
    
    # Course selection conversation handler
    course_selection_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(stream_course_callback, pattern=r"^stream_course_")
        ],
        states={
            BIOLOGY: [CallbackQueryHandler(handle_course_menu_callback)],
            PHYSICS: [CallbackQueryHandler(handle_course_menu_callback)],
            CHEMISTRY: [CallbackQueryHandler(handle_course_menu_callback)],
            MATHEMATICS: [CallbackQueryHandler(handle_course_menu_callback)],
            ENGLISH: [CallbackQueryHandler(handle_course_menu_callback)],
            GEOGRAPHY: [CallbackQueryHandler(handle_course_menu_callback)],
            HISTORY: [CallbackQueryHandler(handle_course_menu_callback)],
        },
        fallbacks=[
            CallbackQueryHandler(handle_course_menu_callback, pattern=r"^back_to_courses$"),
            CallbackQueryHandler(handle_course_menu_callback, pattern=r"^exam_"),
            CallbackQueryHandler(handle_course_menu_callback, pattern=r"^practice_"),
            CallbackQueryHandler(handle_course_menu_callback, pattern=r"^materials_"),
            CallbackQueryHandler(handle_course_menu_callback, pattern=r"^analytics_"),
        ]
    )
    
    return course_selection_handler
