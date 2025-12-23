from app.database.session import SessionLocal
from app.models.user import User
from app.services.payment_service import create_payment
from app.keyboards.payment_keyboard import payment_keyboard

async def payment_menu(update, context):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "💳 Payment Instructions\n\n"
        "Choose your payment method:\n"
        "• Mobile Money\n"
        "• Bank Transfer\n\n"
        "One-time payment amount: $10\n\n"
        "Send your transaction ID or upload screenshot.",
        reply_markup=payment_keyboard()
    )

async def submit_payment(update, context):
    query = update.callback_query
    await query.answer()

    context.user_data["awaiting_payment_proof"] = True

    await query.edit_message_text(
        "📤 Please send your payment proof (transaction ID or screenshot)."
    )

async def receive_payment_proof(update, context):
    if not context.user_data.get("awaiting_payment_proof"):
        await update.message.reply_text("Please use the payment button first to submit your payment proof.")
        return

    # Handle different message types
    if update.message.photo:
        proof = f"Photo uploaded - {update.message.photo[-1].file_id}"
    elif update.message.document:
        proof = f"Document uploaded: {update.message.document.file_name}"
    else:
        proof = update.message.text or "Screenshot uploaded"

    db = SessionLocal()
    user = db.query(User).filter_by(
        telegram_id=update.effective_user.id
    ).first()

    if not user:
        db.close()
        await update.message.reply_text("❌ Error: User not found. Please start with /start command.")
        return

    # Create payment record
    try:
        create_payment(user.id, proof)
        db.close()

        # Clear payment proof state
        context.user_data["awaiting_payment_proof"] = False

        # Confirm to user
        await update.message.reply_text(
            "✅ **Payment Proof Submitted Successfully!**\n\n"
            "📋 **Submission Details:**\n"
            f"• User ID: {user.id}\n"
            f"• Proof Type: {proof[:50]}...\n\n"
            "🔄 **Next Steps:**\n"
            "1. Admin will review your payment\n"
            "2. You'll receive notification upon approval\n"
            "3. Access will be unlocked automatically\n\n"
            "⏱️ Please wait for admin approval. This usually takes a few minutes."
        )

        # Notify admin (if admin is online)
        from app.config.constants import ADMIN_IDS
        from app.keyboards.admin_keyboard import get_admin_main_menu
        
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text="🔔 **NEW PAYMENT SUBMISSION**\n\n"
                         f"📋 **Payment Details:**\n"
                         f"• User: @{user.username or 'N/A'} (ID: {user.telegram_id})\n"
                         f"• Payment ID: {user.id}\n"
                         f"• Proof: {proof[:100]}...\n\n"
                         "💰 Please review in admin panel",
                    reply_markup=get_admin_main_menu()
                )
            except Exception as e:
                print(f"Failed to notify admin {admin_id}: {e}")

    except Exception as e:
        db.close()
        context.user_data["awaiting_payment_proof"] = False
        await update.message.reply_text(f"❌ Error submitting payment proof: {e}")
        print(f"Payment submission error: {e}")
