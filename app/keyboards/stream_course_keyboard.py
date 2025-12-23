"""
Stream-Specific Course Selection Keyboard
Shows different courses based on user's stream AND level during registration
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.session import SessionLocal
from app.models.user import User

def get_stream_courses_keyboard(stream, user_id=None):
    """Get course keyboard based on stream type and user level"""
    
    # Get user level if user_id provided
    user_level = None
    if user_id:
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=user_id).first()
        if user:
            user_level = user.level
        db.close()
    
    # Define courses for each stream - COMMON + STREAM SPECIFIC
    if stream == "natural_science":
        all_courses = [
            ("Biology", "bio"),
            ("Physics", "physics"), 
            ("Chemistry", "chemistry"),
            ("Mathematics", "maths"),
            ("English", "english")
        ]
    elif stream == "social_science":
        all_courses = [
            ("History", "history"),
            ("Geography", "geography"),
            ("Government", "government"),
            ("Economics", "economics"),
            ("Literature", "literature"),
            ("Mathematics", "maths"),
            ("English", "english")
        ]
    else:
        # Default fallback
        all_courses = [
            ("Mathematics", "maths"),
            ("English", "english")
        ]
    
    # Filter courses based on user level - COMMON + STREAM SPECIFIC
    if user_level:
        user_level_lower = user_level.lower()
        stream_lower = stream.lower()
        
        if user_level_lower == "remedial":
            # Remedial users get MATH + ENGLISH (common) + STREAM SPECIFIC
            if stream_lower == "natural_science":
                remedial_courses = ["Mathematics", "English", "Biology", "Physics", "Chemistry"]
            elif stream_lower == "social_science":
                remedial_courses = ["Mathematics", "English", "History", "Geography"]
            else:
                remedial_courses = ["Mathematics", "English"]
            courses = [(name, code) for name, code in all_courses if name in remedial_courses]
            
        elif user_level_lower == "freshman":
            # Freshman users get all courses available in their stream
            courses = all_courses
        else:
            # Unknown level - default to common basic courses
            courses = [(name, code) for name, code in all_courses if name in ["Mathematics", "English"]]
    else:
        # No level info - show common basic courses
        courses = [(name, code) for name, code in all_courses if name in ["Mathematics", "English"]]
    
    # Create keyboard with courses
    keyboard = []
    for course_name, course_code in courses:
        keyboard.append([InlineKeyboardButton(
            f"📚 {course_name}", 
            callback_data=f"stream_course_{course_code}"
        )])
    
    # Add back button
    keyboard.append([InlineKeyboardButton("↩️ Back", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(keyboard)

def get_stream_courses_message(stream, user_id=None):
    """Get appropriate message based on stream and user level"""
    
    # Get user level if user_id provided
    user_level = None
    if user_id:
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=user_id).first()
        if user:
            user_level = user.level
        db.close()
    
    if stream == "natural_science":
        if user_level and user_level.lower() == "remedial":
            return "🧬 Natural Science Stream - Remedial Level\n\n🔰 Remedial Level Access\nCommon Subjects:\n• Mathematics, English\n\nScience Subjects:\n• Biology, Physics, Chemistry"
        elif user_level and user_level.lower() == "freshman":
            return "🧬 Natural Science Stream - Freshman Level\n\n🎓 Freshman Level Access\nAll Natural Science Subjects:\n• Biology, Physics, Chemistry\n• Mathematics, English"
        else:
            return "🧬 Natural Science Stream Courses\n\nSelect your course for exams and practice:"
            
    elif stream == "social_science":
        if user_level and user_level.lower() == "remedial":
            return "🌍 Social Science Stream - Remedial Level\n\n🔰 Remedial Level Access\nCommon Subjects:\n• Mathematics, English\n\nSocial Studies:\n• History, Geography"
        elif user_level and user_level.lower() == "freshman":
            return "🌍 Social Science Stream - Freshman Level\n\n🎓 Freshman Level Access\nAll Social Science Subjects:\n• History, Geography, Government\n• Economics, Literature, Mathematics, English"
        else:
            return "🌍 Social Science Stream Courses\n\nSelect your course for exams and practice:"
    else:
        return "📚 Available Courses\n\nSelect your course for exams and practice:"
