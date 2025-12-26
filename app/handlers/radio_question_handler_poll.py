from app.database.session import SessionLocal
from app.models.answer import Answer
from app.services.scoring_service import finalize_exam, get_detailed_feedback
from app.services.question_service import is_true_false_question
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import PollType
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

def get_timer_duration(course_name):
    """Get timer duration based on course/subject"""
    if not course_name:
        return 60  # Default 1 minute
    
    course_name_lower = course_name.lower()
    
    # Math & Physics get 2 minutes, others get 1 minute
    if any(subject in course_name_lower for subject in ['math', 'physics']):
        return 120  # 2 minutes
    else:
        return 60   # 1 minute

def create_question_data(question, question_number, total_questions, course_name=None):
    """Create question data for poll display - clean options without labels"""
    # Clean the question text to remove any leading "Question X/Y" pattern
    question_text = question.text
    question_text = re.sub(r'^Question \d+/\d+\s*', '', question_text).strip()
    
    if is_true_false_question(question):
        # True/False options for polls
        options = ["TRUE", "FALSE"]
        correct_option_id = 0 if question.correct_answer == "TRUE" else 1
    else:
        # Multiple choice options for polls - clean format (no A), B), etc.)
        options = []
        correct_option_id = 0
        
        if question.option_a:
            # Clean option text without labels
            option_text = question.option_a
            if option_text.startswith(('A)', 'A.', 'A) ')):
                option_text = option_text[2:].strip()  # Remove "A)" or "A." 
            options.append(option_text)
            if question.correct_answer == "A":
                correct_option_id = len(options) - 1
        if question.option_b:
            option_text = question.option_b
            if option_text.startswith(('B)', 'B.', 'B) ')):
                option_text = option_text[2:].strip()
            options.append(option_text)
            if question.correct_answer == "B":
                correct_option_id = len(options) - 1
        if question.option_c:
            option_text = question.option_c
            if option_text.startswith(('C)', 'C.', 'C) ')):
                option_text = option_text[2:].strip()
            options.append(option_text)
            if question.correct_answer == "C":
                correct_option_id = len(options) - 1
        if question.option_d:
            option_text = question.option_d
            if option_text.startswith(('D)', 'D.', 'D) ')):
                option_text = option_text[2:].strip()
            options.append(option_text)
            if question.correct_answer == "D":
                correct_option_id = len(options) - 1

    # Get timer duration for this course
    timer_duration = get_timer_duration(course_name)
    timer_text = f"⏰ {timer_duration//60} minute{'s' if timer_duration > 60 else ''}"
    
    return {
        "question_text": f"📝 Question {question_number}/{total_questions}\n\n{question_text}",
        "options": options,  # Clean options for poll
        "correct_option_id": correct_option_id,
        "question_id": question.id,
        "timer_duration": timer_duration
    }

def create_poll_question(question_data):
    """Create poll data for telegram send_poll"""
    return {
        "question": question_data["question_text"],
        "options": question_data["options"],
        "question_id": question_data["question_id"]
    }

def create_result_keyboard(result_data):
    """Create keyboard for exam results"""
    buttons = [
        [InlineKeyboardButton("📊 View Detailed Results", callback_data=f"view_result_{result_data['result_id']}")],
        [InlineKeyboardButton("🔄 Take Another Exam", callback_data="exams")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ]
    
    return InlineKeyboardMarkup(buttons)

def create_detailed_result_keyboard():
    """Create keyboard for detailed results"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Retake Exam", callback_data="exams")],
        [InlineKeyboardButton("📚 Practice More", callback_data="practice")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ])

async def handle_poll_answer(update, context):
    """Handle poll answer selection"""
    print(f"🔥 POLL ANSWER HANDLER CALLED: user={update.effective_user.id}, poll_id={update.poll_answer.poll_id}")
    
    poll_answer = update.poll_answer
    
    user_id = update.effective_user.id
    poll_id = poll_answer.poll_id
    selected_option = poll_answer.option_ids[0] if poll_answer.option_ids else None
    
    logger.info(f"🔍 POLL ANSWER RECEIVED: User {user_id}, Poll ID: {poll_id}, Selected: {selected_option}")

    # Get user data - find the question that matches this poll
    data = context.user_data

    # Skip if user is not in exam/practice mode
    if "questions" not in data or "index" not in data:
        logger.warning(f"User {user_id} answered poll but not in exam/practice mode")
        return

    # Check if this is the current question's poll
    current_question = data["questions"][data["index"]]
    
    # Verify this is the current poll for the current question
    current_poll_id = data.get("current_poll_id")
    if current_poll_id and str(poll_id) != str(current_poll_id):
        logger.warning(f"Poll ID mismatch: expected {current_poll_id}, got {poll_id}")
        # Continue anyway - this might be an old poll
    
    # Map poll option back to answer letter (A, B, C, D)
    option_letters = ['A', 'B', 'C', 'D']
    selected_answer = option_letters[selected_option] if selected_option is not None else None
    
    # Check if answer is correct
    is_correct = selected_answer == current_question.correct_answer

    logger.info(f"✅ Poll answer processed: Question {current_question.id}, Selected: {selected_answer}, Correct: {is_correct}")

    # Save answer to database
    db = SessionLocal()
    try:
        answer = Answer(
            user_id=data["user_id"],
            exam_id=data.get("exam_id"),
            question_id=current_question.id,
            selected_option=selected_answer,
            is_correct=is_correct
        )
        db.add(answer)
        db.commit()
        logger.info(f"💾 Poll answer saved to database successfully")
    except Exception as e:
        logger.error(f"❌ Error saving poll answer: {e}")
    finally:
        db.close()

    # Cancel any existing timer to prevent conflicts
    if "current_timer" in data and data["current_timer"]:
        data["current_timer"].cancel()
        data["current_timer"] = None

    # Store poll ID for reference
    data["current_poll_id"] = poll_id

    # Move to next question immediately after answer
    data["index"] += 1

    logger.info(f"🔄 Index incremented to {data['index']}, checking completion...")

    # Check if we've completed all questions in current question set
    if data["index"] >= len(data["questions"]):
        logger.info(f"🎉 User {user_id} completed all questions - showing completion")
        # For practice mode, show chapter completion options
        if data.get("practice_mode") and "chapter_completion" in data:
            await show_chapter_completion(update, context, data)
        # For exam mode, complete the exam
        elif "exam_id" in data:
            await complete_exam_or_practice(update, context, data)
        # For practice without chapter tracking, show completion options
        else:
            await show_practice_completion(update, context, data)
    else:
        logger.info(f"➡️ User {user_id} moving to question {data['index'] + 1}/{len(data['questions'])} - calling show_next_question")
        # Show next question immediately
        try:
            await show_next_question(update, context, data)
            logger.info(f"✅ Next question sent successfully")
        except Exception as e:
            logger.error(f"❌ Failed to show next question: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")

async def show_question_as_poll(update, context, data):
    """Display question as Telegram poll"""
    question = data["questions"][data["index"]]
    question_number = data["index"] + 1
    total_questions = len(data["questions"])
    
    # Get course_name from data if available
    course_name = data.get("course_name", None)
    
    # Create question data with course name for timer display
    question_data = create_question_data(question, question_number, total_questions, course_name)
    
    # Create poll data
    poll_data = create_poll_question(question_data)
    
    # Get chat_id - prioritize stored chat_id from data
    chat_id = data.get("chat_id")
    if not chat_id:
        # Fallback to update object if available
        if update and hasattr(update, 'effective_chat') and update.effective_chat:
            chat_id = update.effective_chat.id
        elif update and hasattr(update, 'effective_user') and update.effective_user:
            chat_id = update.effective_user.id
        else:
            logger.error("No chat_id available for showing poll question")
            return

    # Store chat_id in data for future use
    data["chat_id"] = chat_id

    # Send poll question - anonymous poll for single user
    poll_message = await context.bot.send_poll(
        chat_id=chat_id,
        question=poll_data["question"],
        options=poll_data["options"],
        type=PollType.REGULAR,  # Regular poll
        is_anonymous=False,  # Non-anonymous to receive poll answers
        allows_multiple_answers=False,  # Radio button behavior
        open_period=None  # No time limit for poll
    )

    # Store current poll message ID for reference
    data["current_poll_id"] = poll_message.poll.id
    data["current_message_id"] = poll_message.message_id
    
    # Start timer if enabled
    if data.get("use_timer", False):
        timer_duration = question_data["timer_duration"]
        timer_task = asyncio.create_task(question_timer(context, timer_duration))
        data["current_timer"] = timer_task

    logger.info(f"User {data.get('user_id')} - Showing poll question {question_number}/{total_questions}")

async def show_chapter_completion(update, context, data):
    """Show chapter completion options when all questions in a chapter are answered"""
    user_id = data["user_id"]
    question_ids = [q.id for q in data["questions"]]
    
    # Get correct answers from database
    db = SessionLocal()
    try:
        answers = db.query(Answer).filter(
            Answer.user_id == user_id,
            Answer.question_id.in_(question_ids)
        ).all()
        
        correct_answers = sum(1 for answer in answers if answer.is_correct)
        total_questions = len(question_ids)
    finally:
        db.close()
    
    # Calculate score
    percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    message = (
        f"🎉 **Chapter Completed!**\n\n"
        f"📊 **Results:**\n"
        f"• Total Questions: {total_questions}\n"
        f"• Correct Answers: {correct_answers} ✅\n"
        f"• Wrong Answers: {total_questions - correct_answers} ❌\n"
        f"• Score: {percentage:.1f}%\n\n"
        f"What would you like to do next?"
    )
    
    # Create keyboard for chapter completion
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Practice Another Chapter", callback_data="practice_chapter")],
        [InlineKeyboardButton("📖 Practice by Course", callback_data="practice_course")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ])
    
    await context.bot.send_message(
        chat_id=data.get("chat_id"),
        text=message,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    
    # Clear user data for practice session
    for key in ["current_timer", "current_message_id", "current_poll_id", "questions", "index", "practice_mode", "chapter_completion"]:
        data.pop(key, None)

async def show_practice_completion(update, context, data):
    """Show practice session completion options"""
    user_id = data["user_id"]
    question_ids = [q.id for q in data["questions"]]
    
    # Get correct answers from database
    db = SessionLocal()
    try:
        answers = db.query(Answer).filter(
            Answer.user_id == user_id,
            Answer.question_id.in_(question_ids)
        ).all()
        
        correct_answers = sum(1 for answer in answers if answer.is_correct)
        total_questions = len(question_ids)
    finally:
        db.close()
    
    # Calculate score
    percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    message = (
        f"🎉 **Practice Session Completed!**\n\n"
        f"📊 **Results:**\n"
        f"• Total Questions: {total_questions}\n"
        f"• Correct Answers: {correct_answers} ✅\n"
        f"• Wrong Answers: {total_questions - correct_answers} ❌\n"
        f"• Score: {percentage:.1f}%\n\n"
        f"Great job! Keep practicing to improve your skills."
    )
    
    # Create keyboard for practice completion
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Practice More", callback_data="practice")],
        [InlineKeyboardButton("🔄 Take Another Practice", callback_data="practice_chapter")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ])
    
    await context.bot.send_message(
        chat_id=data.get("chat_id"),
        text=message,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    
    # Clear user data for practice session
    for key in ["current_timer", "current_message_id", "current_poll_id", "questions", "index", "practice_mode"]:
        data.pop(key, None)

async def complete_exam_or_practice(update, context, data):
    """Complete exam or practice session"""
    if "exam_id" in data:
        # Real exam completed
        result_data = finalize_exam(data["user_id"], data["exam_id"])
        
        status = "✅ PASSED" if result_data["passed"] else "❌ FAILED"
        message = (
            f"🎉 **Exam Completed!**\n\n"
            f"📊 **Results:**\n"
            f"• Total Questions: {result_data['total_questions']}\n"
            f"• Correct Answers: {result_data['correct_answers']} ✅\n"
            f"• Wrong Answers: {result_data['wrong_answers']} ❌\n"
            f"• Score: {result_data['percentage']:.1f}%\n"
            f"• Status: {status}"
        )
        
        # Send completion message with keyboard
        await context.bot.send_message(
            chat_id=data.get("chat_id"),
            text=message,
            parse_mode="Markdown",
            reply_markup=create_result_keyboard(result_data)
        )
        
    else:
        # Practice session completed
        await context.bot.send_message(
            chat_id=data.get("chat_id"),
            text="🎉 Practice session completed!\n\nKeep practicing to improve your skills!",
            reply_markup=create_detailed_result_keyboard()
        )

async def show_next_question(update, context, data):
    """Show the next question as poll"""
    print(f"🎯 SHOW_NEXT_QUESTION CALLED: index={data.get('index')}, total={len(data.get('questions', []))}")
    
    question = data["questions"][data["index"]]
    question_number = data["index"] + 1
    total_questions = len(data["questions"])

    # Get course_name from data if available
    course_name = data.get("course_name", None)

    # Create question data with course name for timer display
    question_data = create_question_data(question, question_number, total_questions, course_name)

    # Get chat_id - prioritize stored chat_id from data
    chat_id = data.get("chat_id")
    if not chat_id:
        # Fallback to update object if available
        if update and hasattr(update, 'effective_chat') and update.effective_chat:
            chat_id = update.effective_chat.id
        elif update and hasattr(update, 'effective_user') and update.effective_user:
            chat_id = update.effective_user.id
        else:
            logger.error("No chat_id available for showing next question")
            return

    # Store chat_id in data for future use
    data["chat_id"] = chat_id

    # Create poll data
    poll_data = create_poll_question(question_data)

    # Send poll question to the chat
    poll_message = await context.bot.send_poll(
        chat_id=chat_id,
        question=poll_data["question"],
        options=poll_data["options"],
        type=PollType.REGULAR,  # Regular poll
        is_anonymous=False,  # Non-anonymous to receive poll answers
        allows_multiple_answers=False,  # Radio button behavior
        open_period=None  # No time limit for poll
    )

    # Store current poll message ID for reference
    data["current_poll_id"] = poll_message.poll.id
    data["current_message_id"] = poll_message.message_id

    # Start timer if enabled
    if data.get("use_timer", False):
        timer_duration = question_data["timer_duration"]
        timer_task = asyncio.create_task(question_timer(context, timer_duration))
        data["current_timer"] = timer_task

    logger.info(f"User {data.get('user_id')} - Showing poll question {question_number}/{total_questions}")

async def start_exam_with_polls(update, context, data):
    """Start exam or practice with poll-style questions"""
    data["index"] = 0
    data["current_message_id"] = None
    data["current_poll_id"] = None
    
    # Store chat_id for poll sending
    if update and update.effective_chat:
        data["chat_id"] = update.effective_chat.id
    elif update and update.effective_user:
        data["chat_id"] = update.effective_user.id
    else:
        # Fallback to user ID if chat info not available
        data["chat_id"] = data.get("user_id")
    
    # Show first question as poll
    await show_question_as_poll(update, context, data)

async def question_timer(context, seconds):
    """Timer for question polls"""
    await asyncio.sleep(seconds)
    
    data = context.user_data
    if "questions" in data and data["index"] < len(data["questions"]) and "current_poll_id" in data:
        # Time's up - move to next question without answer
        question = data["questions"][data["index"]]
        
        # Save empty answer
        db = SessionLocal()
        answer = Answer(
            user_id=data["user_id"],
            exam_id=data.get("exam_id"),
            question_id=question.id,
            selected_option=None,
            is_correct=False
        )
        db.add(answer)
        db.commit()
        db.close()
        
        data["index"] += 1
        data["current_poll_id"] = None
        data["current_timer"] = None  # Clear timer state
        
        if data["index"] >= len(data["questions"]):
            # Session completed due to timeout
            await complete_exam_or_practice(None, context, data)
        else:
            # Show next question on timeout
            try:
                # Send timeout message and next question
                await context.bot.send_message(
                    chat_id=data.get("chat_id"),
                    text="⏰ Time's up! Moving to next question..."
                )
                
                # Show the next question
                await show_question_as_poll(None, context, data)
            except Exception as e:
                logger.error(f"Error showing next question after timeout: {e}")
                logger.info("Question timeout - unable to show next question")

async def show_detailed_result(update, context):
    """Show detailed exam result with feedback"""
    try:
        result_id = int(update.message.text.split("_")[1])
    except (IndexError, ValueError):
        await update.message.reply_text("Invalid result ID format. Use /result_{id}")
        return

    db = SessionLocal()
    from app.models.result import Result
    result = db.query(Result).filter_by(id=result_id).first()

    if not result or result.user_id != update.effective_user.id:
        await update.message.reply_text("Result not found or access denied.")
        db.close()
        return

    feedback = get_detailed_feedback(result.user_id, result.exam_id)

    status = "✅ PASSED" if result.percentage >= 70 else "❌ FAILED"

    message = (
        f"📋 **Detailed Exam Result**\n\n"
        f"📊 **Overall Score:** {result.score}/{len(feedback)} ({result.percentage:.1f}%)\n"
        f"🎯 **Status:** {status}\n\n"
        f"📝 **Question Review:**\n\n"
    )

    for i, item in enumerate(feedback[:10], 1):  # Limit to 10 questions
        correct_mark = "✅" if item["is_correct"] else "❌"
        message += f"{i}. {correct_mark} {item['question_text']}\n"
        message += f"   Your answer: {item['user_answer'] or 'Not answered'}\n"
        message += f"   Correct: {item['correct_answer']}\n\n"

    if len(feedback) > 10:
        message += f"... and {len(feedback) - 10} more questions"

    await update.message.reply_text(
        message, 
        parse_mode="Markdown",
        reply_markup=create_detailed_result_keyboard()
    )
    db.close()

# Legacy function aliases for backward compatibility
async def start_exam_with_buttons(update, context, data):
    """Legacy function - redirect to poll version"""
    return await start_exam_with_polls(update, context, data)

# Additional helper functions for question management
def format_question_text(question, question_number, total_questions):
    """Format question text for display"""
    return f"📝 Question {question_number}/{total_questions}\n\n{question.text}"

def get_option_letter(option_id):
    """Convert option ID to letter (0=A, 1=B, 2=C, 3=D)"""
    letters = ['A', 'B', 'C', 'D']
    return letters[option_id] if option_id < len(letters) else 'A'
