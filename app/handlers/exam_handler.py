from app.keyboards.course_keyboard import course_keyboard
from app.keyboards.payment_keyboard import payment_keyboard
from app.database.session import SessionLocal
from app.models.user import User

async def start_exam(update, context):
    query = update.callback_query
    await query.answer()

    # Check access status
    user_id = query.from_user.id
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

    await query.edit_message_text(
        "Select a course:",
        reply_markup=course_keyboard()
    )

