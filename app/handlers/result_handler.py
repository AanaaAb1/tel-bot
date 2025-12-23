from app.services.result_services import get_user_exam_history

async def user_result_history(update, context):
    user_id = update.effective_user.id
    history = get_user_exam_history(user_id)

    if not history:
        await update.message.reply_text("📄 No past exams found.")
        return

    messages = []
    for e in history:
        messages.append(
            f"Course: {e['course']}\n"
            f"Exam: {e['exam']}\n"
            f"Score: {e['score']}\n"
            f"Percentage: {e['percentage']:.1f}%\n"
            f"Completed: {e['completed_at']}\n"
            "---------------------"
        )

    await update.message.reply_text("\n".join(messages))

    await update.message.reply_text("\n".join(messages))