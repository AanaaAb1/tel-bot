from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.database.session import SessionLocal
from app.models.user import User
from app.services.user_service import get_or_create_user
from app.keyboards.main_menu import main_menu
from app.keyboards.stream_keyboard import stream_keyboard

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /register command"""
    print(f"Register command received from {update.message.from_user.id}")

    # Get or create user
    user = get_or_create_user(update.message.from_user)
    
    if user.level and user.stream:
        # User is already registered
        if user.access == "LOCKED":
            # User registered but not paid - redirect to payment
            from app.keyboards.payment_keyboard import payment_keyboard
            await update.message.reply_text(
                "👋 **Welcome back!**\n\n"
                "You are registered but need to complete payment to access features.\n\n"
                "💳 **Please proceed with payment:**",
                reply_markup=payment_keyboard(),
                parse_mode="Markdown"
            )
        else:
            # User registered and paid - show main menu
            await update.message.reply_text(
                "✅ **You are already registered and approved!**\n\n"
                "You can access all features. Choose an option:",
                reply_markup=main_menu(update.message.from_user.id),
                parse_mode="Markdown"
            )
    else:
        # Start registration process
        await update.message.reply_text(
            "👋 **Welcome to Smart Test Exam!**\n\n"
            "To complete your registration, please select your level:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔰 Remedial", callback_data="level_remedial")],
                [InlineKeyboardButton("🎓 Freshman", callback_data="level_freshman")],
            ]),
            parse_mode="Markdown"
        )

async def handle_registration_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle registration level/stream selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    
    if not user:
        await query.edit_message_text("❌ User not found. Please try /register again.")
        db.close()
        return
    
    if data.startswith("level_"):
        # Level selection
        level = data.replace("level_", "")
        user.level = level
        db.commit()
        
        # Now ask for stream
        await query.edit_message_text(
            f"📚 **Level Selected: {level.title()}**\n\n"
            "Now select your stream:",
            reply_markup=stream_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data.startswith("stream_"):
        # Stream selection
        stream = data.replace("stream_", "")
        user.stream = stream
        # Keep access LOCKED - user must pay first
        db.commit()
        
        # Registration complete - redirect to payment
        from app.keyboards.payment_keyboard import payment_keyboard
        await query.edit_message_text(
            f"🎉 **Registration Complete!** 🎉\n\n"
            f"✅ **Level:** {user.level.title()}\n"
            f"✅ **Stream:** {stream.title()}\n\n"
            f"🔒 **Next Step: Payment Required**\n\n"
            f"You must complete payment to access all features.\n\n"
            f"💳 **Payment Details:**\n"
            f"• Amount: Specify Amount\n"
            f"• Method: Bank Transfer / Mobile Money\n"
            f"• After payment, admin will approve your access\n\n"
            f"Please proceed with payment to unlock access:",
            reply_markup=payment_keyboard(),
            parse_mode="Markdown"
        )
    
    db.close()
