import random
import string
import uuid
from app.database.session import SessionLocal
from app.models.user import User
from app.models.referral import Referral
from app.keyboards.main_menu import main_menu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

def generate_referral_code():
    """Generate a unique referral code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

async def profile_menu(update, context):
    """Display user profile with referral information"""
    try:
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        
        if not user:
            db.close()
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(
                    "❌ **Profile not found**\n\nPlease register first.",
                    reply_markup=main_menu(update.effective_user.id)
                )
            else:
                await update.message.reply_text(
                    "❌ **Profile not found**\n\nPlease register first.",
                    reply_markup=main_menu(update.effective_user.id)
                )
            return

        # Generate referral code if not exists
        if not user.referral_code:
            user.referral_code = generate_referral_code()
            db.commit()

        # Get referral statistics
        completed_referrals = db.query(Referral).filter_by(
            referrer_id=user.id, 
            status="COMPLETED"
        ).count()

        # Get total commission earned
        total_commission = db.query(Referral).filter_by(
            referrer_id=user.id, 
            commission_paid=True
        ).count() * 30  # 30 ETB per successful referral

        # Build profile message
        message_text = f"👤 **Your Profile**\n\n"
        message_text += f"🆔 **User ID:** {user.telegram_id}\n"
        message_text += f"👤 **Name:** {user.full_name or 'Not set'}\n"
        message_text += f"📅 **Joined:** {user.join_time.strftime('%Y-%m-%d') if user.join_time else 'Unknown'}\n"
        message_text += f"🎓 **Level:** {user.level or 'Not set'}\n"
        message_text += f"📚 **Stream:** {user.stream or 'Not set'}\n"
        message_text += f"💰 **Payment Status:** {user.payment_status}\n"
        message_text += f"🔒 **Access:** {user.access}\n\n"
        
        message_text += f"🎯 **Referral Program**\n"
        message_text += f"✅ **Successful Referrals:** {completed_referrals}\n"
        message_text += f"💵 **Total Commission:** {total_commission} ETB\n"
        message_text += f"📋 **Your Referral Code:** `{user.referral_code}`\n\n"

        # Generate invitation link with fallback
        bot_username = context.bot.username
        if not bot_username:
            bot_username = "your_bot_username"  # Fallback - should be configured
        invitation_link = f"https://t.me/{bot_username}?start=ref_{user.referral_code}"

        message_text += f"🔗 **Your Invitation Link:**\n"
        message_text += f"`{invitation_link}`\n\n"

        message_text += f"💡 **How it works:**\n"
        message_text += f"• Share your invitation link with friends\n"
        message_text += f"• When they register and pay, you get 30 ETB\n"
        message_text += f"• Track your earnings here in your profile\n"

        # Create keyboard for profile actions
        keyboard = [
            [InlineKeyboardButton("📋 Copy Referral Code", callback_data=f"copy_code_{user.referral_code}")],
            [InlineKeyboardButton("🔗 Copy Invitation Link", callback_data=f"copy_link_{invitation_link}")],
            [InlineKeyboardButton("📊 View Referral History", callback_data=f"referral_history_{user.id}")],
            [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        if hasattr(update, 'callback_query') and update.callback_query:
            try:
                await update.callback_query.edit_message_text(
                    message_text,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Error editing message: {e}")
                await update.callback_query.answer("Profile updated!")
        else:
            await update.message.reply_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

        db.close()
        
    except Exception as e:
        print(f"Error in profile_menu: {e}")
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.answer("Error loading profile")
        else:
            await update.message.reply_text("❌ Error loading profile. Please try again.")

async def copy_referral_code(update, context):
    """Copy referral code to clipboard"""
    try:
        referral_code = update.callback_query.data.split("_")[-1]
        
        await update.callback_query.answer(f"📋 Referral Code: {referral_code}")
        
        # Send the code in a separate message for easy copying
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"📋 **Your Referral Code:**\n\n`{referral_code}`\n\n👆 *Copy the code above to share with friends!*"
        )
    except Exception as e:
        print(f"Error in copy_referral_code: {e}")
        await update.callback_query.answer("Error copying code")

async def copy_invitation_link(update, context):
    """Copy invitation link to clipboard"""
    try:
        invitation_link = update.callback_query.data.split("_", 2)[-1]  # Get everything after "copy_link_"
        
        await update.callback_query.answer(f"🔗 Invitation Link copied!")
        
        # Send the link in a separate message for easy copying
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"🔗 **Your Invitation Link:**\n\n`{invitation_link}`\n\n👆 *Copy the link above and share with friends!*"
        )
    except Exception as e:
        print(f"Error in copy_invitation_link: {e}")
        await update.callback_query.answer("Error copying link")

async def view_referral_history(update, context):
    """View detailed referral history"""
    try:
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        
        if not user:
            db.close()
            await update.callback_query.answer("User not found")
            return

        # Get all referrals made by this user
        referrals = db.query(Referral).filter_by(referrer_id=user.id).order_by(Referral.created_at.desc()).all()

        if not referrals:
            message_text = "📊 **Referral History**\n\nYou haven't made any referrals yet.\n\nStart sharing your invitation link to earn 30 ETB per successful referral!"
        else:
            message_text = "📊 **Referral History**\n\n"
            
            for i, referral in enumerate(referrals[:10], 1):  # Show last 10 referrals
                referred_user = db.query(User).filter_by(id=referral.referred_id).first()
                referred_name = referred_user.full_name if referred_user else "Unknown User"
                
                status_emoji = "✅" if referral.status == "COMPLETED" else "⏳"
                status_text = "Completed" if referral.status == "COMPLETED" else "Pending"
                
                commission_text = f" +{referral.commission_earned} ETB" if referral.commission_paid else ""
                
                message_text += f"{i}. {status_emoji} **{referred_name}**\n"
                message_text += f"   📅 {referral.created_at.strftime('%Y-%m-%d') if referral.created_at else 'Unknown'}\n"
                message_text += f"   💰 Status: {status_text}{commission_text}\n\n"

        keyboard = [
            [InlineKeyboardButton("⬅️ Back to Profile", callback_data="profile")],
            [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        db.close()
        
    except Exception as e:
        print(f"Error in view_referral_history: {e}")
        await update.callback_query.answer("Error loading history")

async def handle_referral_registration(user_id, referral_code):
    """Handle referral when a user registers with a referral code"""
    db = SessionLocal()
    
    try:
        # Find the referrer by referral code
        referrer = db.query(User).filter_by(referral_code=referral_code).first()
        if not referrer:
            db.close()
            return None
            
        # Find the newly registered user
        new_user = db.query(User).filter_by(telegram_id=user_id).first()
        if not new_user:
            db.close()
            return None
            
        # Check if this referral already exists
        existing_referral = db.query(Referral).filter_by(
            referrer_id=referrer.id,
            referred_id=new_user.id
        ).first()
        
        if existing_referral:
            db.close()
            return None
            
        # Create new referral record
        new_referral = Referral(
            referrer_id=referrer.id,
            referred_id=new_user.id,
            status="PENDING"
        )
        
        # Update referrer stats
        referrer.total_referrals = (referrer.total_referrals or 0) + 1
        
        db.add(new_referral)
        db.commit()
        
        referral_id = new_referral.id
        db.close()
        return referral_id
        
    except Exception as e:
        print(f"Error handling referral: {e}")
        db.close()
        return None

def process_referral_commission_sync(user_id):
    """Sync version - Process successful referral payment without Telegram API calls"""
    db = SessionLocal()
    
    try:
        # Find the user who just paid
        user = db.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            db.close()
            return None
            
        # Find pending referrals for this user
        pending_referrals = db.query(Referral).filter_by(
            referred_id=user.id,
            status="PENDING"
        ).all()
        
        total_commission_awarded = 0
        referrals_completed = []
        
        for referral in pending_referrals:
            # Update referral status
            referral.status = "COMPLETED"
            referral.completed_at = datetime.utcnow()
            referral.commission_paid = True
            
            # Award commission to referrer
            referrer = db.query(User).filter_by(id=referral.referrer_id).first()
            if referrer:
                referrer.total_commission = (referrer.total_commission or 0) + 30
                total_commission_awarded += 30
                referrals_completed.append({
                    'referrer_id': referrer.id,
                    'referrer_telegram_id': referrer.telegram_id,
                    'referrer_name': referrer.full_name,
                    'commission': 30
                })
        
        db.commit()
        
        print(f"Referral commission processed for user {user_id}: {total_commission_awarded} ETB awarded")
        return {
            'total_commission': total_commission_awarded,
            'referrals_completed': referrals_completed,
            'user_id': user_id
        }
        
    except Exception as e:
        print(f"Error processing referral payment: {e}")
        db.rollback()
        return None
        
    finally:
        db.close()

async def process_successful_referral_payment(user_id, context):
    """Async version - Process successful referral payment with notifications"""
    try:
        # First process the commission sync
        result = process_referral_commission_sync(user_id)
        
        if result and result['referrals_completed']:
            # Notify all referrers
            for referral_data in result['referrals_completed']:
                try:
                    await context.bot.send_message(
                        chat_id=referral_data['referrer_telegram_id'],
                        text=f"🎉 **Commission Earned!**\n\n"
                             f"✅ Your referral has paid!\n"
                             f"💰 You earned: **30 ETB**\n\n"
                             f"📊 Total Commission: **{referral_data['referrer_name'] or 'Unknown'}**\n\n"
                             f"Keep sharing your link to earn more! 🚀"
                    )
                    print(f"Successfully notified referrer {referral_data['referrer_telegram_id']} of commission")
                except Exception as e:
                    print(f"Failed to notify referrer {referral_data['referrer_telegram_id']}: {e}")
        
        return result
        
    except Exception as e:
        print(f"Error in async referral payment processing: {e}")
        return None
