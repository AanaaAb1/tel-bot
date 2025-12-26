from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.session import SessionLocal
from app.models.course import Course

def get_admin_course_selection_keyboard():
    """Course selection keyboard for question management - dynamically loaded from database"""
    db = SessionLocal()
    try:
        courses = db.query(Course).order_by(Course.name).all()
        keyboard = []
        
        # Add course buttons dynamically (2 per row)
        for i, course in enumerate(courses):
            course_display = f"📚 {course.name}"
            callback_data = f"admin_select_course_{course.name}"
            
            if i % 2 == 0:  # Start new row
                keyboard.append([InlineKeyboardButton(course_display, callback_data=callback_data)])
            else:  # Add to existing row
                keyboard[-1].append(InlineKeyboardButton(course_display, callback_data=callback_data))
        
        # Add "No Course" option as fallback
        keyboard.append([InlineKeyboardButton("🚫 No Course", callback_data="admin_select_course_No Course")])
        
        return InlineKeyboardMarkup(keyboard)
    finally:
        db.close()

def get_admin_chapter_selection_keyboard():
    """Chapter selection keyboard for question management (1-10 chapters)"""
    keyboard = []
    
    # Add chapter buttons (2 per row for better layout)
    for i in range(1, 11):
        if i % 2 == 1:  # Odd numbers start new row
            if i == 1:
                keyboard.append([InlineKeyboardButton(f"📖 Chapter {i}", callback_data=f"admin_select_chapter_{i}")])
            else:
                keyboard.append([
                    InlineKeyboardButton(f"📖 Chapter {i-1}", callback_data=f"admin_select_chapter_{i-1}"),
                    InlineKeyboardButton(f"📖 Chapter {i}", callback_data=f"admin_select_chapter_{i}")
                ])
    
    # Add No Chapter option
    keyboard.append([InlineKeyboardButton("🚫 No Chapter", callback_data="admin_select_chapter_No Chapter")])
    
    # Add back button
    keyboard.append([InlineKeyboardButton("⬅️ Back to Course Selection", callback_data="admin_select_course_back")])
    
    return InlineKeyboardMarkup(keyboard)

def get_admin_question_step_keyboard(step, show_skip=False):
    """Step-by-step question addition keyboard"""
    if step == "question_text":
        keyboard = [
            [InlineKeyboardButton("✅ Done", callback_data="admin_question_done")]
        ]
    elif step == "option_a":
        keyboard = [
            [InlineKeyboardButton("✅ Done", callback_data="admin_question_done")]
        ]
    elif step == "option_b":
        keyboard = [
            [InlineKeyboardButton("✅ Done", callback_data="admin_question_done")]
        ]
    elif step == "option_c":
        keyboard = [
            [InlineKeyboardButton("✅ Done", callback_data="admin_question_done")]
        ]
    elif step == "option_d":
        keyboard = [
            [InlineKeyboardButton("✅ Done", callback_data="admin_question_done")]
        ]
    elif step == "option_e":
        if show_skip:
            keyboard = [
                [InlineKeyboardButton("✅ Done", callback_data="admin_question_done")],
                [InlineKeyboardButton("⏭️ Skip", callback_data="admin_question_skip")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("✅ Done", callback_data="admin_question_done")]
            ]
    else:
        keyboard = []
    
    # Add cancel option
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="admin_question_cancel")])
    
    return InlineKeyboardMarkup(keyboard)

def get_admin_question_confirm_keyboard():
    """Confirmation keyboard for question addition"""
    keyboard = [
        [InlineKeyboardButton("✅ Save Question", callback_data="admin_question_save")],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_question_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_question_cancel_keyboard():
    """Cancel question addition keyboard"""
    keyboard = [
        [InlineKeyboardButton("❌ Yes, Cancel", callback_data="admin_question_confirm_cancel")],
        [InlineKeyboardButton("✅ No, Continue", callback_data="admin_question_continue")]
    ]
    return InlineKeyboardMarkup(keyboard)

