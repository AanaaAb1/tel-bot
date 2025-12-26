from app.database.session import SessionLocal
from app.models.answer import Answer
from app.models.result import Result
from app.services.scoring_service import finalize_exam, get_detailed_feedback
from app.keyboards.exam_keyboard import question_keyboard, format_question_text
from app.services.question_service import is_true_false_question
import asyncio

async def answer_question(update, context):
    query = update.callback_query
    await query.answer()

    data = context.user_data
    question = data["questions"][data["index"]]

    selected = query.data.replace("ans_", "")

    # Handle true/false questions
    if is_true_false_question(question):
        is_correct = selected == question.correct_answer
    else:
        is_correct = selected == question.correct_answer

    # Cancel any existing timer for this question to prevent conflicts
    if "current_timer" in data and data["current_timer"]:
        data["current_timer"].cancel()
        data["current_timer"] = None

    db = SessionLocal()
    answer = Answer(
        user_id=data["user_id"],
        exam_id=data.get("exam_id"),  # Include exam_id if available (for exams, not practice)
        question_id=question.id,
        selected_option=selected,
        is_correct=is_correct
    )
    db.add(answer)
    db.commit()
    db.close()

    data["index"] += 1

    if data["index"] >= len(data["questions"]):
        # Exam completed
        if "exam_id" in data:
            result_data = finalize_exam(data["user_id"], data["exam_id"])

            status = "✅ PASSED" if result_data["passed"] else "❌ FAILED"
            message = (
                f"🎉 **Exam Completed!**\n\n"
                f"📊 **Results:**\n"
                f"• Total Questions: {result_data['total_questions']}\n"
                f"• Correct Answers: {result_data['correct_answers']} ✅\n"
                f"• Wrong Answers: {result_data['wrong_answers']} ❌\n"
                f"• Score: {result_data['percentage']:.1f}%\n"
                f"• Status: {status}\n\n"
                f"💡 Want detailed feedback? Use /result_{result_data['result_id']}"
            )

            await query.edit_message_text(
                message,
                parse_mode="Markdown"
            )
        else:
            # Practice mode completed
            await query.edit_message_text(
                "🎉 Practice session completed!\n\nKeep practicing to improve your skills!"
            )
    else:
        # Show next question immediately
        next_q = data["questions"][data["index"]]
        question_text = format_question_text(next_q)

        await query.edit_message_text(
            question_text,
            reply_markup=question_keyboard(next_q)
        )

        # Start new timer for next question if enabled
        if data.get("use_timer", False):
            timer_task = asyncio.create_task(question_timer(context, 30))  # 30 second timer
            data["current_timer"] = timer_task

async def show_detailed_result(update, context):
    """Show detailed exam result with feedback"""
    try:
        result_id = int(update.message.text.split("_")[1])
    except (IndexError, ValueError):
        await update.message.reply_text("Invalid result ID format. Use /result_{id}")
        return

    db = SessionLocal()
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

    for i, item in enumerate(feedback[:10], 1):  # Limit to 10 questions to avoid message length limits
        correct_mark = "✅" if item["is_correct"] else "❌"
        message += f"{i}. {correct_mark} {item['question_text']}\n"
        message += f"   Your answer: {item['user_answer'] or 'Not answered'}\n"
        message += f"   Correct: {item['correct_answer']}\n\n"

    if len(feedback) > 10:
        message += f"... and {len(feedback) - 10} more questions"

    await update.message.reply_text(message, parse_mode="Markdown")
    db.close()

async def question_timer(context, seconds):
    """Timer for individual questions"""
    await asyncio.sleep(seconds)

    data = context.user_data
    if "questions" in data and data["index"] < len(data["questions"]):
        # Time's up - auto-submit with no answer
        question = data["questions"][data["index"]]

        db = SessionLocal()
        answer = Answer(
            user_id=data["user_id"],
            exam_id=data.get("exam_id"),  # Include exam_id if available
            question_id=question.id,
            selected_option=None,
            is_correct=False
        )
        db.add(answer)
        db.commit()
        db.close()

        data["index"] += 1

        if data["index"] >= len(data["questions"]):
            # Session completed
            if "exam_id" in data:
                # Exam completed due to timeout
                result_data = finalize_exam(data["user_id"], data["exam_id"])
                status = "✅ PASSED" if result_data["passed"] else "❌ FAILED"
                message = (
                    f"⏰ **Time's Up - Exam Completed!**\n\n"
                    f"📊 **Results:**\n"
                    f"• Total Questions: {result_data['total_questions']}\n"
                    f"• Correct Answers: {result_data['correct_answers']} ✅\n"
                    f"• Wrong Answers: {result_data['wrong_answers']} ❌\n"
                    f"• Score: {result_data['percentage']:.1f}%\n"
                    f"• Status: {status}\n\n"
                    f"💡 Want detailed feedback? Use /result_{result_data['result_id']}"
                )
                await context.bot.send_message(
                    chat_id=context.user_data.get("chat_id"),
                    text=message,
                    parse_mode="Markdown"
                )
            else:
                # Practice mode completed
                await context.bot.send_message(
                    chat_id=context.user_data.get("chat_id"),
                    text="⏰ Time's up! Practice session completed."
                )
        else:
            # Show next question
            next_q = data["questions"][data["index"]]
            question_text = format_question_text(next_q)

            await context.bot.send_message(
                chat_id=context.user_data.get("chat_id"),
                text=f"⏰ Time's up for previous question!\n\n{question_text}",
                reply_markup=question_keyboard(next_q)
            )

            # Start timer for next question
            if data.get("use_timer", False):
                timer_task = asyncio.create_task(question_timer(context, 30))
                data["current_timer"] = timer_task
