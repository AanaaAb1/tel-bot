from app.database.session import SessionLocal
from app.models.user import User
from app.models.course import Course
from app.models.chapter import Chapter
from app.services.course_service import get_course_by_id, get_course_by_name, get_courses_by_code
from app.services.question_service import get_questions_by_chapter
from app.keyboards.main_menu import main_menu
from app.handlers.radio_question_handler_poll import show_question_as_poll
from app.keyboards.payment_keyboard import payment_keyboard
from app.keyboards.admin_question_keyboard import get_admin_course_selection_keyboard
from app.config.constants import ADMIN_IDS
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

def get_difficulty_keyboard():
    """Create difficulty selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("🟢 Easy", callback_data="difficulty_easy")],
        [InlineKeyboardButton("🟡 Intermediate", callback_data="difficulty_intermediate")],
        [InlineKeyboardButton("🔴 Advanced", callback_data="difficulty_advanced")],
        [InlineKeyboardButton("🔙 Back to Courses", callback_data="courses")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_difficulty_text(course_name):
    """Get text for difficulty selection"""
    return f"📚 {course_name}\n\n🎯 Select difficulty level:\n\n🟢 Easy - Basic concepts and fundamentals\n🟡 Intermediate - Moderate complexity\n🔴 Advanced - Challenging problems"

def get_chapters_by_course(course_id):
    """Get all chapters for a specific course"""
    db = SessionLocal()
    try:
        chapters = db.query(Chapter).filter(Chapter.course_id == course_id).order_by(Chapter.name).all()
        return chapters
    except Exception as e:
        print(f"Error getting chapters for course {course_id}: {e}")
        return []
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

    # NEW FLOW: Show difficulty selection instead of chapters
    # This implements: Course → Difficulty → Chapters → Questions
    
    # Store selected course info for later use
    context.user_data['selected_course'] = course.name
    context.user_data['selected_course_id'] = course.id
    
    # Show difficulty selection
    keyboard = get_difficulty_keyboard()
    text = get_difficulty_text(course.name)
    
    await query.edit_message_text(text, reply_markup=keyboard)

async def select_difficulty(update, context):
    """Handle difficulty selection - new function"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    difficulty = query.data.replace("difficulty_", "")  # easy, intermediate, advanced
    
    # Get stored course info
    course_name = context.user_data.get('selected_course')
    course_id = context.user_data.get('selected_course_id')
    
    if not course_name or not course_id:
        # Fallback if course info is missing
        await query.edit_message_text(
            "❌ Error: Course selection lost. Please start again.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Courses", callback_data="courses")
            ]])
        )
        return

    # Get chapters for this course
    chapters = get_chapters_by_course(course_id)
    
    # Sort chapters numerically by extracting the chapter number from the name
    def get_chapter_number(chapter_name):
        try:
            # Extract number from "Chapter X" format
            return int(chapter_name.split()[-1])
        except:
            return 0
    
    chapters.sort(key=lambda x: get_chapter_number(x.name))

    # Build chapter selection message with difficulty context
    difficulty_emoji = {"easy": "🟢", "intermediate": "🟡", "advanced": "🔴"}
    difficulty_text = difficulty.title()
    
    message = f"📚 {course_name}\n"
    message += f"{difficulty_emoji.get(difficulty, '⚪')} {difficulty_text} Difficulty\n\n"
    message += "📖 Select Chapter:\n"
    
    keyboard_buttons = []
    if chapters:
        # Display chapters in 2-column format
        for i in range(0, len(chapters), 2):
            row = []
            
            # Left column
            if i < len(chapters):
                chapter = chapters[i]
                message += f"{i+1:2d}. {chapter.name:<20}"
                row.append(InlineKeyboardButton(f"📝 {chapter.name}", callback_data=f"start_exam_{chapter.id}_{difficulty}"))
            
            # Right column
            if i+1 < len(chapters):
                chapter = chapters[i+1]
                message += f"  |  {i+2:2d}. {chapter.name}\n"
                row.append(InlineKeyboardButton(f"📝 {chapter.name}", callback_data=f"start_exam_{chapter.id}_{difficulty}"))
            else:
                message += "\n"
            
            keyboard_buttons.append(row)
        
        # Add padding if odd number of chapters
        if len(chapters) % 2 == 1:
            keyboard_buttons.append([InlineKeyboardButton(" ", callback_data="ignore")])
    else:
        message += "No chapters available yet.\n"

    # Add back buttons
    keyboard_buttons.append([InlineKeyboardButton("⬅️ Back to Difficulty", callback_data=f"exam_course_{course_id}")])
    keyboard_buttons.append([InlineKeyboardButton("🔙 Back to Courses", callback_data="courses")])
    keyboard_buttons.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await query.edit_message_text(message, reply_markup=keyboard)

async def start_exam_selected(update, context):
    """Start exam for selected chapter with difficulty context"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    
    # Parse callback data: start_exam_{chapter_id}_{difficulty}
    callback_parts = query.data.replace("start_exam_", "").split("_")
    if len(callback_parts) >= 2:
        chapter_id = int(callback_parts[0])
        difficulty = callback_parts[1]  # easy, intermediate, advanced
    else:
        # Fallback for old format (without difficulty)
        chapter_id = int(query.data.replace("start_exam_", ""))
        difficulty = "easy"  # Default difficulty

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

    # Get questions for this chapter and difficulty
    # Note: The question service needs to be updated to handle difficulty filtering
    questions = get_questions_by_chapter(chapter_id, limit=None)  # Get all questions for chapter

    if not questions:
        await query.edit_message_text(
            "There are no questions for this chapter at the selected difficulty level.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="courses")]])
        )
        return

    # Initialize exam session with difficulty context
    context.user_data["user_id"] = query.from_user.id
    context.user_data["chat_id"] = query.message.chat_id
    context.user_data["chapter_id"] = chapter_id
    context.user_data["difficulty"] = difficulty
    context.user_data["questions"] = questions
    context.user_data["index"] = 0
    context.user_data["use_timer"] = False  # Can be made configurable

    # Start exam with radio-style poll questions
    await show_question_as_poll(update, context, context.user_data)
