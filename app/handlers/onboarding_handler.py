from app.database.session import SessionLocal
from app.models.user import User
from app.keyboards.stream_keyboard import stream_keyboard
from app.keyboards.main_menu import main_menu

async def onboarding(update, context):
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    user = db.query(User).filter_by(
        telegram_id=query.from_user.id
    ).first()

    if query.data.startswith("level_"):
        user.level = query.data.replace("level_", "")
        db.commit()
        await query.edit_message_text(
            "Select your stream:",
            reply_markup=stream_keyboard()
        )

    elif query.data.startswith("stream_"):
        user.stream = query.data.replace("stream_", "")
        db.commit()
        await query.edit_message_text(
            "Registration completed ✅",
            reply_markup=main_menu(query.from_user.id)
        )

    db.close()