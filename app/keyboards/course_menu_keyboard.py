"""
Course Menu Keyboard
Provides course-specific menu options after course selection
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_course_menu_keyboard():
    """Get the course menu keyboard with options for selected course"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Exams", callback_data="exam_course_menu"),
            InlineKeyboardButton("🎯 Practice", callback_data="practice_course_menu")
        ],
        [
            InlineKeyboardButton("📚 Materials", callback_data="materials_course_menu"),
            InlineKeyboardButton("📊 Analytics", callback_data="analytics_course_menu")
        ],
        [
            InlineKeyboardButton("⬅️ Back to Courses", callback_data="back_to_courses"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_course_menu_message(course_name):
    """Get the course menu message for the selected course"""
    return f"""
🎓 **{course_name} Course Menu**

Choose what you'd like to do with {course_name}:

📝 **Exams** - Take exams for {course_name}
🎯 **Practice** - Practice questions for {course_name}
📚 **Materials** - Study materials for {course_name}
📊 **Analytics** - View your performance in {course_name}

Select an option below:
"""

def get_course_menu_keyboard_with_back(course_name):
    """Get course menu keyboard with back button to course selection"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Exams", callback_data=f"exam_{course_name.lower()}"),
            InlineKeyboardButton("🎯 Practice", callback_data=f"practice_{course_name.lower()}")
        ],
        [
            InlineKeyboardButton("📚 Materials", callback_data=f"materials_{course_name.lower()}"),
            InlineKeyboardButton("📊 Analytics", callback_data=f"analytics_{course_name.lower()}")
        ],
        [
            InlineKeyboardButton("⬅️ Back to Courses", callback_data="back_to_courses")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
