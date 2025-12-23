from app.database.session import SessionLocal
from app.models.answer import Answer
from app.services.scoring_service import finalize_exam, get_detailed_feedback
from app.keyboards.radio_exam_keyboard import create_poll_question, create_result_keyboard, create_detailed_result_keyboard
import asyncio
import logging

logger = logging.getLogger(__name__)

async def handle_poll_answer(update, context):
    """Handle poll answer selection"""
    poll_answer = update.poll_answer
    user_id = update.effective_user.id
    poll_id = poll_answer.poll_id
    
    # Get user data
    data = context.user_data
    
    # Skip if user is not in exam/practice mode
    if "current_poll_id" not in data or data["current_poll_id"] != poll_id:
        return
    
    # Get selected option
    selected_option_ids = poll_answer.option_ids
    if not selected_option_ids:
        return
    
    selected_option_id = selected_option_ids[0]  # Take first selected option
    question = data["questions"][data["index"]]
    
    # Convert option ID to letter (A=0, B=1, C=2, D=3)
    option_letters = ['A', 'B', 'C', 'D']
    selected_option = option_letters[selected_option_id] if selected_option_id < len(option_letters) else 'A'
    
    # Check if answer is correct
    is_correct = selected_option == question.correct_option
    
    # Save answer to database
    db = SessionLocal()
    answer = Answer(
        user_id=data["user_id"],
        exam_id=data.get("exam_id"),
        question_id=question.id,
        selected_option=selected_option,
        is_correct=is_correct
    )
    db.add(answer)
    db.commit()
    db.close()
    
    logger.info(f"User {user_id} answered question {question.id}: {selected_option} (Correct: {is_correct})")
    
    # Cancel any existing poll timer to prevent conflicts
    if "current_poll_timer" in data and data["current_poll_timer"]:
        data["current_poll_timer"].cancel()
        data["current_poll_timer"] = None
    
    # Move to next question immediately
    data["index"] += 1
    data["current_poll_id"] = None  # Clear current poll
    
    if data["index"] >= len(data["questions"]):
        # Exam/Practice completed
        await complete_exam_or_practice(update, context, data)
    else:
        # Show next question immediately
        await show_next_question(update, context, data)

async def show_question_as_poll(update, context, data):
    """Display question as a poll"""
    question = data["questions"][data["index"]]
    question_number = data["index"] + 1
    total_questions = len(data["questions"])
    
    # Create poll question
    poll_data = create_poll_question(question, question_number, total_questions)
    
    # Send poll - handle both cases (with and without update object)
    if update is not None:
        # Normal case - user answered or it's the first question
        message = await update.effective_message.reply_poll(
            question=poll_data["question"],
            options=poll_data["options"],
            type="quiz",  # This makes it a quiz with correct answer
            correct_option_id=poll_data["correct_option_id"],
            is_anonymous=False
        )
    else:
        # Timeout case - send poll to specific chat
        chat_id = data.get("chat_id")
        if chat_id:
            message = await context.bot.send_poll(
                chat_id=chat_id,
                question=poll_data["question"],
                options=poll_data["options"],
                type="quiz",  # This makes it a quiz with correct answer
                correct_option_id=poll_data["correct_option_id"],
                is_anonymous=False
            )
        else:
            logger.error("No chat_id available for showing poll")
            return
    
    # Store current poll ID for answer tracking
    data["current_poll_id"] = message.poll.id
    
    # Start timer if enabled
    if data.get("use_timer", False):
        timer_task = asyncio.create_task(poll_timer(context, 30))  # 30 second timer
        data["current_poll_timer"] = timer_task

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
    """Show the next question as a poll"""
    await show_question_as_poll(update, context, data)

async def start_exam_with_polls(update, context, data):
    """Start exam or practice with poll-style questions"""
    data["index"] = 0
    data["current_poll_id"] = None
    
    # Show first question
    await show_question_as_poll(update, context, data)

async def poll_timer(context, seconds):
    """Timer for poll questions"""
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
        data["current_poll_timer"] = None  # Clear timer state
        
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
                logger.info("Poll timeout - unable to show next question")

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

# Additional helper functions for poll management
def format_poll_question_text(question, question_number, total_questions):
    """Format question text for poll display"""
    return f"📝 Question {question_number}/{total_questions}\n\n{question.text}"

def get_option_letter(option_id):
    """Convert option ID to letter (0=A, 1=B, 2=C, 3=D)"""
    letters = ['A', 'B', 'C', 'D']
    return letters[option_id] if option_id < len(letters) else 'A'
