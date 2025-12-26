from app.database.session import SessionLocal
from app.models.user import User
from app.models.course import Course
from app.models.exam import Exam
from app.services.course_service import get_course_by_id, get_course_by_name, get_courses_by_code
from app.services.question_service import get_questions_by_chapter
from app.keyboards.main_menu import main_menu
from app.handlers.radio_question_handler import start_exam_with_polls
from app.keyboards.payment_keyboard import payment_keyboard
from app.keyboards.admin_question_keyboard import get_admin_course_selection_keyboard
from app.config.constants import ADMIN_IDS
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

def get_exams_by_course(course_id):
    """Get all exam chapters for a specific course"""
    db = SessionLocal()
    try:
        exams = db.query(Exam).filter(Exam.course_id == course_id).order_by(Exam.name).all()
        return exams
    except Exception as e:
        print(f"Error getting exams for course {course_id}: {e}")
        return []
    finally:
        db.close()

def get_exam_by_id(exam_id):
    """Get exam by ID"""
    db = SessionLocal()
    try:
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        return exam
    except Exception as e:
        print(f"Error getting exam {exam_id}: {e}")
        return None
    finally:
        db.close()

async def select_course(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    
    # CRITICAL: Admins ALWAYS skip payment checks and get immediate access
    if user_id in ADMIN_IDS:
        # Admin gets immediate access - no payment required!
        pass
    else:
        # Check payment status for regular users only
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=user_id).first()
        db.close()

        if not user or user.access == "LOCKED":
            await query.edit_message_text(
                "⚠️ Access Restricted\n\n"
                "You must complete payment to access exams.\n\n"
                "Please proceed to payment and wait for admin approval.",
                reply_markup=payment_keyboard()
            )
            return

    # Handle both numeric IDs and course codes
    callback_data = query.data.replace("exam_course_", "")
    
    # Try to parse as integer first (legacy format)
    try:
        course_id = int(callback_data)
        course = get_course_by_id(course_id)
    except ValueError:
        # Not a number, treat as course code
        courses = get_courses_by_code(callback_data)
        if not courses:
            # Create a user-friendly message for missing courses
            missing_courses = ['geography', 'history', 'government', 'economics', 'literature']
            if callback_data.lower() in missing_courses:
                await query.edit_message_text(
                    f"⚠️ Course Unavailable\n\n"
                    f"The course '{callback_data.title()}' is not available in our exam system yet.\n\n"
                    f"📚 Currently Available Courses:\n"
                    f"• Mathematics\n"
                    f"• Physics\n" 
                    f"• Chemistry\n"
                    f"• Biology\n"
                    f"• English\n\n"
                    f"Please select from the available courses above.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📚 View All Courses", callback_data="courses")],
                        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
                    ])
                )
            else:
                await query.edit_message_text(
                    "Course not found.\n\nPlease try selecting from the available courses.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📚 View All Courses", callback_data="courses")],
                        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
                    ])
                )
            return
        course = courses[0]  # Get the first course matching the code
        
    if not course:
        await query.edit_message_text(
            "Course not found.\n\nPlease try selecting from the available courses.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📚 View All Courses", callback_data="courses")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
            ])
        )
        return

    # Get chapters (exams) for this course
    exams = get_exams_by_course(course.id)

    # Build course content message
    message = f"📚 {course.name}\n\n"
    if course.description:
        message += f"{course.description}\n\n"

    message += "📖 Chapters:\n"
    keyboard_buttons = []
    if exams:
        # Display chapters in 2-column format
        for i in range(0, len(exams), 2):
            row = []
            
            # Left column
            if i < len(exams):
                exam = exams[i]
                message += f"{i+1:2d}. {exam.name:<20}"
                row.append(InlineKeyboardButton(f"📝 {exam.name}", callback_data=f"start_exam_{exam.id}"))
            
            # Right column
            if i+1 < len(exams):
                exam = exams[i+1]
                message += f"  |  {i+2:2d}. {exam.name}\n"
                row.append(InlineKeyboardButton(f"📝 {exam.name}", callback_data=f"start_exam_{exam.id}"))
            else:
                message += "\n"
            
            keyboard_buttons.append(row)
        
        # Add padding if odd number of chapters
        if len(exams) % 2 == 1:
            keyboard_buttons.append([InlineKeyboardButton(" ", callback_data="ignore")])
    else:
        message += "No chapters available yet.\n"

    # Add Add Question button for admins (only show if user is admin)
    if user_id in ADMIN_IDS:
        keyboard_buttons.append([InlineKeyboardButton("➕ Add Question", callback_data=f"admin_add_question_{course.id}_{course.name}")])

    # Add back button
    keyboard_buttons.append([InlineKeyboardButton("⬅️ Back to Courses", callback_data="courses")])
    keyboard_buttons.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await query.edit_message_text(message, reply_markup=keyboard)

async def start_exam_selected(update, context):
    """Start exam for selected chapter"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    chapter_id = int(query.data.replace("start_exam_", ""))

    # CRITICAL: Admins ALWAYS skip payment checks
    if user_id not in ADMIN_IDS:
        # Check payment status for regular users only
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        db.close()

        if not user or user.access == "LOCKED":
            await query.edit_message_text(
                "⚠️ Access Restricted\n\n"
                "You must complete payment to access exams.\n\n"
                "Please proceed to payment and wait for admin approval.",
                reply_markup=payment_keyboard()
            )
            return

    # Get questions for this chapter
    questions = get_questions_by_chapter(chapter_id, limit=None)  # Get all questions for chapter

    if not questions:
        await query.edit_message_text(
            "No questions available for this chapter yet.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="courses")]])
        )
        return

    # Initialize exam session
    context.user_data["user_id"] = query.from_user.id
    context.user_data["chat_id"] = query.message.chat_id
    context.user_data["chapter_id"] = chapter_id
    context.user_data["questions"] = questions
    context.user_data["index"] = 0
    context.user_data["use_timer"] = False  # Can be made configurable

    # Start exam with radio-style questions
    await start_exam_with_polls(update, context, context.user_data)

