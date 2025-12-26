from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.database.session import SessionLocal
from app.models.user import User
from app.services.user_service import get_or_create_user
from app.keyboards.main_menu import main_menu
from app.config.constants import ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Start command received from {update.message.from_user.id}")

    # Check user in database
    user = get_or_create_user(update.message.from_user)

    if not (user.level and user.stream):
        # User not registered - start onboarding
        keyboard = [
            [InlineKeyboardButton("Remedial", callback_data="level_remedial")],
            [InlineKeyboardButton("Freshman", callback_data="level_freshman")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welcome! Please select your level:", reply_markup=reply_markup
        )
    elif user.access == "LOCKED":
        # CRITICAL: Admins ALWAYS skip payment checks
        if update.message.from_user.id in ADMIN_IDS:
            # Admin gets immediate access - no payment required!
            await update.message.reply_text(
                "Welcome back! Choose an option:",
                reply_markup=main_menu(update.message.from_user.id)
            )
        else:
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
        # User registered and approved - show main menu
        await update.message.reply_text(
            "Welcome back! Choose an option:",
            reply_markup=main_menu(update.message.from_user.id)
        )
