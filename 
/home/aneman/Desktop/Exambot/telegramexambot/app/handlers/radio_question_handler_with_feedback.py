
from app.database.session import SessionLocal
from app.models.answer import Answer
from app.services.scoring_service import finalize_exam, get_detailed_feedback
from app.services.question_service import is_true_false_question
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import logging

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
    """Create question data for button display"""
    if is_true_false_question(question):
        # True/False options
        options = ["TRUE", "FALSE"]
        correct_option_id = 0 if question.correct_answer == "TRUE" else 1
    else:
        # Multiple choice options
        options = []
        correct_option_id = 0
        
        if question.option_a:
            options.append(question.option_a)
            if question.correct_answer == "A":
                correct_option_id = len(options) - 1
        if question.option_b:
            options.append(question.option_b)
            if question.correct_answer == "B":
                correct_option_id = len(options) - 1
        if question.option_c:
            options.append(question.option_c)
            if question.correct_answer == "C":
                correct_option_id = len(options) - 1
        if question.option_d:
            options.append(question.option_d)
            if question.correct_answer == "D":
                correct_option_id = len(options) - 1

    # Add A, B, C, D labels if not already present
    labeled_options = []
    for i, option in enumerate(options):
        if not option.startswith(('A)', 'B)', 'C)', 'D)', 'A.', 'B.', 'C.', 'D.')):
            label = chr(65 + i)  # A, B, C, D
            labeled_options.append(f"{label}) {option}")
        else:
            labeled_options.append(option)

    # Get timer duration for this course
    timer_duration = get_timer_duration(course_name)
    timer_text = f"⏰ {timer_duration//60} minute{'s' if timer_duration > 60 else ''}"
    
    return {
        "question_text": f"📝 Question {question_number}/{total_questions} ({timer_text})\n\n{question.text}",
        "options": labeled_options,
        "correct_option_id": correct_option_id,
        "question_id": question.id,
        "timer_duration": timer_duration
    }

def create_question_keyboard(question_data):
    """Create inline keyboard for question options"""
    buttons = []
    
    # Create buttons for each option
    for i, option in enumerate(question_data["options"]):
        # Extract option letter (A, B, C, D) for callback data
        option_letter = chr(65 + i)  # A, B, C, D
        callback_data = f"answer_{question_data['question_id']}_{option_letter}"
        buttons.append([InlineKeyboardButton(option, callback_data=callback_data)])
    
    return InlineKeyboardMarkup(buttons)

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

def create_feedback_message(question_data, selected_option, correct_option_letter, is_correct):
    """Create feedback message showing correct answer and user selection"""
    # Status emoji and text
    status_emoji = "✅" if is_correct else "❌"
    status_text = "CORRECT!" if is_correct else "INCORRECT"
    
    # Create feedback header
    feedback = f"{status_emoji} **{status_text}**\n\n"
    feedback += f"📝 **Question:**\n{question_data['question_text']}\n\n"
    
    # Show all options with highlighting
    feedback += "🔘 **Your Answer:**\n"
    for i, option in enumerate(question_data["options"]):
        option_letter = chr(65 + i)  # A, B, C, D
        if option_letter == selected_option:
            if is_correct:
                feedback += f"✅ {option} ← *Your choice*\n"
            else:
                feedback += f"❌ {option} ← *Your choice*\n"
        elif option_letter == correct_option_letter:
            feedback += f"✅ {option} ← *Correct answer*\n"
        else:
            feedback += f"⚪ {option}\n"
    
    # Show explanation if available
    feedback += "\n💡 **Explanation:**\n"
    feedback += "Review the concept and try similar questions to improve your understanding.\n"
    
    return feedback

async def handle_button_answer(update, context):
    """Handle button answer selection with immediate feedback and auto-advance"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    callback_data = query.data
    
    logger.info(f"🔍 BUTTON ANSWER RECEIVED: User {user_id}, Callback: {callback_data}")

    # Parse callback data: "answer_{question_id}_{option_letter}"
    try:
        parts = callback_data.split("_")
        if len(parts) != 3 or parts[0] != "answer":
            logger.warning(f"Invalid callback data format: {callback_data}")
            return
            
        question_id = int(parts[1])
        selected_option = parts[2]
    except (ValueError, IndexError):
        logger.warning(f"Failed to parse callback data: {callback_data}")
        return

    # Get user data
    data = context.user_data

    # Skip if user is not in exam/practice mode
    if "questions" not in data or "index" not in data:
        logger.warning(f"User {user_id} answered question but not in exam/practice mode")
        return

    # Get current question
    question = data["questions"][data["index"]]
    
    # Verify the question ID matches
    if question.id != question_id:
        logger.warning(f"Question ID mismatch: expected {question.id}, got {question_id}")
        # Continue anyway - this might be an old callback
    
    # Check if answer is correct
    is_correct = selected_option == question.correct_answer
    correct_option_letter = question.correct_answer

    logger.info(f"✅ Answer processed: Question {question.id}, Selected: {selected_option}, Correct: {is_correct}")

    # Create question data for feedback
    question_number = data["index"] + 1
    total_questions = len(data["questions"])
    course_name = data.get("course_name", None)
    question_data = create_question_data(question, question_number, total_questions, course_name)
    question_data["question_id"] = question.id
    
    # Create and show feedback message immediately
    feedback_message = create_feedback_message(question_data, selected_option, correct_option_letter, is_correct)
    
    # Send feedback message with "Next Question" button
    await query.edit_message_text(
        text=feedback_message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➡️ Next Question", callback_data=f"next_question_{question.id}")]
        ])
    )
    
    # Save answer to database
    db = SessionLocal()
    try:
        answer = Answer(
            user_id=data["user_id"],
            exam_id=data.get("exam_id"),
            question_id=question.id,
            selected_option=selected_option,
            is_correct=is_correct
        )
        db.add(answer)
        db.commit()
        logger.info(f"💾 Answer saved to database successfully")
    except Exception as e:
        logger.error(f"❌ Error saving answer: {e}")
    finally:
        db.close()

    # Cancel any existing timer to prevent conflicts
    if "current_timer" in data and data["current_timer"]:
        data["current_timer"].cancel()
        data["current_timer"] = None

    # Schedule auto-advance to next question after 3 seconds
    logger.info(f"⏱️ Auto-advancing to next question in 3 seconds...")
    await asyncio.sleep(3)
    
    # Move to next question
    data["index"] += 1

    # Check if we've completed all questions
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
        logger.info(f"➡️ User {user_id} moving to question {data['index'] + 1}/{len(data['questions'])}")
        # Show next question automatically
        try:
            await show_next_question(update, context, data)
            logger.info(f"✅ Next question sent successfully")
        except Exception as e:
            logger.error(f"❌ Failed to show next question: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")

async def show_question_as_button(update, context, data):
    """Display question as button inline keyboard"""
    question = data["questions"][data["index"]]
    question_number = data["index"] + 1
    total_questions = len(data["questions"])
    
    # Get course_name from data if available
    course_name = data.get("course_name", None)
    
    # Create question data with course name for timer display
    question_data = create_question_data(question, question_number, total_questions, course_name)
    
    # Create keyboard for the question
    keyboard = create_question_keyboard(question_data)
    
    # Send question with buttons - handle both cases (with and without update object)
    if update is not None:
        # Normal case - user answered or it's the first question
        message = await update.effective_message.reply_text(
            text=question_data["question_text"],
            reply_markup=keyboard,
            parse_mode=None  # No markdown to avoid formatting issues
        )
    else:
        # Timeout case - send question to specific chat
        chat_id = data.get("chat_id")
        if chat_id:
            message = await context.bot.send_message(
                chat_id=chat_id,
                text=question_data["question_text"],
                reply_markup=keyboard,
                parse_mode=None  # No markdown to avoid formatting issues
            )
        else:
            logger.error("No chat_id available for showing question")
            return
    
    # Store current question message ID for reference
    data["current_message_id"] = message.message_id
    
    # Start timer if enabled
    if data.get("use_timer", False):
        timer_duration = question_data["timer_duration"]
        timer_task = asyncio.create_task(question_timer(context, timer_duration))
        data["current_timer"] = timer_task

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
    
    await update.effective_message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    
    # Clear user data for practice session
    for key in ["current_timer", "current_message_id", "questions", "index", "practice_mode", "chapter_completion"]:
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
    
    await update.effective_message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    
    # Clear user data for practice session
    for key in ["current_timer", "current_message_id", "questions", "index", "practice_mode"]:
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
        await update.effective_message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=create_result_keyboard(result_data)
        )
        
    else:
        # Practice session completed
        await update.effective_message.reply_text(
            "🎉 Practice session completed!\n\nKeep practicing to improve your skills!",
            reply_markup=create_detailed_result_keyboard()
        )

async def show_next_question(update, context, data):
    """Show the next question as button keyboard"""
    # For showing next question after an answer, we need to send to the same chat
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

    # Create keyboard for the question
    keyboard = create_question_keyboard(question_data)

    # Send question to the chat directly (not as a reply to button click)
    message = await context.bot.send_message(
        chat_id=chat_id,
        text=question_data["question_text"],
        reply_markup=keyboard,
        parse_mode=None  # No markdown to avoid formatting issues
    )

    # Store current question message ID for reference
    data["current_message_id"] = message.message_id

    # Start timer if enabled
    if data.get("use_timer", False):
        timer_duration = question_data["timer_duration"]
        timer_task = asyncio.create_task(question_timer(context, timer_duration))
        data["current_timer"] = timer_task

    logger.info(f"User {data.get('user_id')} - Showing question {question_number}/{total_questions}")

async def start_exam_with_buttons(update, context, data):
    """Start exam or practice with button-style questions"""
    data["index"] = 0
    data["current_message_id"] = None
    
    # Store chat_id for next question sending
    if update and update.effective_chat:
        data["chat_id"] = update.effective_chat.id
    elif update and update.effective_user:
        data["chat_id"] = update.effective_user.id
    else:
        # Fallback to user ID if chat info not available
        data["chat_id"] = data.get("user_id")
    
    # Show first question
    await show_question_as_button(update, context, data)

async def question_timer(context, seconds):
    """Timer for question buttons"""
    await asyncio.sleep(seconds)
    
    data = context.user_data
    if "questions" in data and data["index"] < len(data["questions"]) and "current_message_id" in data:
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
        data["current_message_id"] = None
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
                await show_question_as_button(None, context, data)
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
async def start_exam_with_polls(update, context, data):
    """Legacy function - redirect to button version"""
    return await start_exam_with_buttons(update, context, data)

# Additional helper functions for question management
def format_question_text(question, question_number, total_questions):
    """Format question text for display"""
    return f"📝 Question {question_number}/{total_questions}\n\n{question.text}"

def get_option_letter(option_id):
    """Convert option ID to letter (0=A, 1=B, 2=C, 3=D)"""
    letters = ['A', 'B', 'C', 'D']
    return letters[option_id] if option_id < len(letters) else 'A'
