from app.keyboards.course_keyboard import course_keyboard
from app.utils.access_control import enforce_payment_access

async def start_exam(update, context):
    query = update.callback_query
    await query.answer()

    # Enforce payment access control
    has_access = await enforce_payment_access(update, context)
    if not has_access:
        return

    await query.edit_message_text(
        "Select a course:",
        reply_markup=course_keyboard()
    )
