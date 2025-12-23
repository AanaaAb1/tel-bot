import os
from app.database.session import SessionLocal
from app.models.user import User
from app.models.payment import Payment
from app.models.exam import Exam
from app.models.question import Question
from app.services.payment_service import approve_payment, reject_payment
from app.config.constants import ADMIN_IDS
from app.keyboards.admin_keyboard import (
    get_admin_main_menu,
    get_admin_questions_menu,
    get_admin_export_menu,
    get_admin_confirm_delete,
    get_payment_approval_keyboard
)
from app.keyboards.main_menu import main_menu
from telegram import InputFile, InlineKeyboardButton, InlineKeyboardMarkup
import io
from datetime import datetime

# Helper function for safe message editing
async def safe_edit_message_text(update, text, reply_markup=None):
    """Safely edit a message with fallback to sending new message"""
    try:
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        else:
            # For regular messages, send new message
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error editing message: {e}")
        # Simple fallback: send new message
        try:
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup
            )
        except Exception as fallback_error:
            print(f"Error in fallback message sending: {fallback_error}")

# Admin panel main menu
async def admin_panel(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.answer("Access denied.")
            await safe_edit_message_text(update, "Access denied.")
        else:
            await update.message.reply_text("Access denied.")
        return

    message_text = "🛠️ Admin Panel\n\nWelcome to the admin dashboard!"
    
    if hasattr(update, 'callback_query') and update.callback_query:
        await safe_edit_message_text(update, 
            message_text,
            reply_markup=get_admin_main_menu()
        )
    else:
        await update.message.reply_text(
            message_text,
            reply_markup=get_admin_main_menu()
        )

# View all users
async def admin_users(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.answer("Access denied.")
            await safe_edit_message_text(update, "Access denied.")
        else:
            await update.message.reply_text("Access denied.")
        return

    db = SessionLocal()
    users = db.query(User).all()

    if not users:
        message_text = "👥 User Management\n\nNo users found."
    else:
        message_text = "👥 All Users:\n\n"
        for user in users:
            status = "✅ Unlocked" if user.access == "unlocked" else "🔒 Locked"
            payment_status = user.payment_status if hasattr(user, 'payment_status') else "Unknown"
            message_text += f"🆔 ID: {user.telegram_id}\n"
            message_text += f"👤 Name: {user.full_name or 'Not set'}\n"
            message_text += f"🔗 Username: @{user.username or 'None'}\n"
            message_text += f"📊 Status: {status}\n"
            message_text += f"💰 Payment: {payment_status}\n"
            message_text += f"📅 Joined: {user.created_at.strftime('%Y-%m-%d') if user.created_at else 'Unknown'}\n\n"
            message_text += "➖" * 20 + "\n\n"

    if hasattr(update, 'callback_query') and update.callback_query:
        await safe_edit_message_text(update, 
            message_text,
            reply_markup=get_admin_main_menu()
        )
    else:
        await update.message.reply_text(
            message_text,
            reply_markup=get_admin_main_menu()
        )

    db.close()

# Payment management - FIXED VERSION with interactive buttons
async def admin_payments(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.answer("Access denied.")
            await safe_edit_message_text(update, "Access denied.")
        else:
            await update.message.reply_text("Access denied.")
        return

    db = SessionLocal()
    payments = db.query(Payment).filter_by(status="PENDING").all()

    if not payments:
        message_text = "💰 Payment Management\n\nNo pending payments found."
        if hasattr(update, 'callback_query') and update.callback_query:
            await safe_edit_message_text(update, 
                message_text,
                reply_markup=get_admin_main_menu()
            )
        else:
            await update.message.reply_text(
                message_text,
                reply_markup=get_admin_main_menu()
            )
        db.close()
        return

    payment_list = "💰 Pending Payments:\n\n"
    
    # Create buttons for each payment
    payment_buttons = []
    
    for payment in payments:
        # Get user info for better display
        user = db.query(User).filter_by(id=payment.user_id).first()
        username = f"@{user.username}" if user and user.username else f"ID: {user.telegram_id}" if user else "Unknown User"
        
        payment_list += f"🆔 Payment ID: {payment.id}\n"
        payment_list += f"👤 User: {username}\n"
        payment_list += f"📋 Proof: {payment.proof[:80]}{'...' if len(payment.proof) > 80 else ''}\n"
        payment_list += f"📅 Date: {payment.created_at.strftime('%Y-%m-%d %H:%M') if payment.created_at else 'Unknown'}\n\n"
        payment_list += "➖" * 30 + "\n\n"
        
        # Add button for this payment
        payment_buttons.append([InlineKeyboardButton(f"📋 View Payment #{payment.id}", callback_data=f"view_payment_{payment.id}")])
    
    # Add back button
    payment_buttons.append([InlineKeyboardButton("⬅️ Back to Admin Menu", callback_data="admin_back_main")])
    
    # Create the keyboard markup
    reply_markup = InlineKeyboardMarkup(payment_buttons)

    if hasattr(update, 'callback_query') and update.callback_query:
        await safe_edit_message_text(update, 
            payment_list,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            payment_list,
            reply_markup=reply_markup
        )

    db.close()

# Enhanced payment details view with screenshot
async def admin_view_payment_details(update, context):
    """View individual payment with screenshot and approve/reject buttons"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    try:
        # Extract payment ID from callback data
        callback_data = update.callback_query.data
        if callback_data.startswith("view_payment_"):
            payment_id = int(callback_data.split("_")[-1])
        else:
            await update.callback_query.answer("Invalid payment ID.")
            return
        
        db = SessionLocal()
        payment = db.query(Payment).filter_by(id=payment_id).first()
        user = db.query(User).filter_by(id=payment.user_id).first() if payment else None
        
        if not payment:
            await safe_edit_message_text(
                update,
                "❌ Payment not found.",
                reply_markup=get_admin_main_menu()
            )
            db.close()
            return

        # Create payment details message
        username = f"@{user.username}" if user and user.username else f"ID: {user.telegram_id}" if user else "Unknown User"
        
        message_text = f"💰 Payment Details - ID: {payment.id}\n\n"
        message_text += f"👤 User: {username}\n"
        message_text += f"📅 Submitted: {payment.created_at.strftime('%Y-%m-%d %H:%M') if payment.created_at else 'Unknown'}\n"
        message_text += f"💳 Amount: $10 (One-time payment)\n"
        message_text += f"📋 Payment Proof: {payment.proof}\n\n"
        message_text += "Review the payment proof above and approve or reject:"

        # Send payment screenshot if available
        if payment.proof.startswith("Photo uploaded"):
            try:
                # Extract file_id from the proof text
                file_id = payment.proof.replace("Photo uploaded - ", "")
                
                await update.callback_query.answer("📸 Loading payment proof...")
                
                # Send the photo
                await context.bot.send_photo(
                    chat_id=update.effective_user.id,
                    photo=file_id,
                    caption=f"💰 Payment Proof for ID: {payment.id}\n\n"
                           f"👤 User: {username}\n"
                           f"📅 Date: {payment.created_at.strftime('%Y-%m-%d %H:%M') if payment.created_at else 'Unknown'}\n\n"
                           f"Please review and approve/reject:",
                    reply_markup=get_payment_approval_keyboard(payment_id)
                )
            except Exception as e:
                # Fallback to text message if photo fails
                await safe_edit_message_text(
                    update,
                    message_text,
                    reply_markup=get_payment_approval_keyboard(payment_id)
                )
        else:
            # Send text message with approve/reject buttons
            await safe_edit_message_text(
                update,
                message_text,
                reply_markup=get_payment_approval_keyboard(payment_id)
            )
            
        db.close()
        
    except Exception as e:
        await safe_edit_message_text(
            update,
            f"❌ Error loading payment details: {str(e)}",
            reply_markup=get_admin_main_menu()
        )

# FIXED approve payment - NO SESSION DETACHMENT ISSUE
async def admin_approve_payment(update, context):
    """Approve payment with enhanced user notification"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    try:
        payment_id = int(update.callback_query.data.split("_")[-1])
        
        # Get user info for notification BEFORE approving
        db = SessionLocal()
        payment = db.query(Payment).filter_by(id=payment_id).first()
        user = db.query(User).filter_by(id=payment.user_id).first() if payment else None
        db.close()
        
        # Approve the payment
        success = approve_payment(payment_id)
        
        if success and user:
            # Confirm to admin
            await safe_edit_message_text(update, 
                f"✅ Payment {payment_id} APPROVED\n\n"
                f"🎉 User access has been unlocked!\n"
                f"📧 User has been notified of the approval.",
                reply_markup=get_admin_main_menu()
            )

            # Enhanced notification to user
            try:
                # Send celebration message
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text="🎉🎉🎉 CONGRATULATIONS! 🎉🎉🎉\n\n"
                         "🎯 YOUR PAYMENT HAS BEEN APPROVED! 🎯\n\n"
                         "✅ FULL ACCESS UNLOCKED!\n\n"
                         "🚀 Welcome to Premium Access!\n\n"
                         "🎮 What you can now enjoy:\n"
                         "• 📚 Unlimited Practice Tests - Master any subject\n"
                         "• 📝 Official Exams - Get certified\n"
                         "• 📖 Complete Study Materials - All courses available\n"
                         "• 📊 Detailed Results & Analytics - Track your progress\n"
                         "• 🎓 Certificates - Earn official qualifications\n"
                         "• 🔥 Priority Support - Get help when you need it\n\n"
                         "🌟 Your journey to success starts NOW!\n\n"
                         "Go ahead and explore all the amazing features available to you! 🎊"
                )
                
                # Send main menu with all options available
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text="🎯 Choose your next adventure:",
                    reply_markup=main_menu(user.telegram_id)
                )
                
                print(f"✅ Successfully notified user {user.telegram_id} of payment approval")
                
            except Exception as e:
                print(f"❌ Failed to notify user {user.telegram_id}: {e}")
                # Send message to admin about notification failure
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=f"⚠️ Payment approved but failed to notify user:\n"
                         f"User ID: {user.telegram_id}\n"
                         f"Please manually notify the user."
                )
        elif success:
            await safe_edit_message_text(update, 
                f"✅ Payment {payment_id} APPROVED\n\n"
                f"⚠️ But user not found for notification.",
                reply_markup=get_admin_main_menu()
            )
        else:
            await safe_edit_message_text(update, 
                f"❌ Payment {payment_id} NOT FOUND\n\n"
                f"The payment may have already been processed or doesn't exist.",
                reply_markup=get_admin_main_menu()
            )
    except Exception as e:
        await safe_edit_message_text(update, 
            f"❌ Error approving payment:\n{str(e)}",
            reply_markup=get_admin_main_menu()
        )

# FIXED reject payment - NO SESSION DETACHMENT ISSUE
async def admin_reject_payment(update, context):
    """Reject payment with enhanced user notification"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    try:
        payment_id = int(update.callback_query.data.split("_")[-1])
        
        # Get user info for notification BEFORE rejecting
        db = SessionLocal()
        payment = db.query(Payment).filter_by(id=payment_id).first()
        user = db.query(User).filter_by(id=payment.user_id).first() if payment else None
        db.close()
        
        # Reject the payment
        success = reject_payment(payment_id)
        
        if success and user:
            # Confirm to admin
            await safe_edit_message_text(update, 
                f"❌ Payment {payment_id} REJECTED\n\n"
                f"User has been notified of the rejection.",
                reply_markup=get_admin_main_menu()
            )

            # Enhanced notification to user
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text="❌ Payment Rejected ❌\n\n"
                         "Unfortunately, your payment proof could not be verified.\n\n"
                         "🔍 Possible reasons:\n"
                         "• Unclear or incomplete payment screenshot\n"
                         "• Invalid transaction details\n"
                         "• Payment not yet processed\n\n"
                         "🔄 What you can do now:\n"
                         "• ✅ Resubmit with a clearer payment screenshot\n"
                         "• 📞 Contact your bank to verify the transaction\n"
                         "• 💬 Message admin for specific guidance\n\n"
                         "📧 Support: Don't worry, we're here to help!\n"
                         "Contact support for assistance with your payment."
                )
            except Exception as e:
                print(f"Failed to notify user {user.telegram_id}: {e}")
        elif success:
            await safe_edit_message_text(update, 
                f"❌ Payment {payment_id} REJECTED\n\n"
                f"⚠️ But user not found for notification.",
                reply_markup=get_admin_main_menu()
            )
        else:
            await safe_edit_message_text(update, 
                f"❌ Payment {payment_id} not found or could not be rejected",
                reply_markup=get_admin_main_menu()
            )
    except Exception as e:
        await safe_edit_message_text(update, 
            f"❌ Error rejecting payment:\n{str(e)}",
            reply_markup=get_admin_main_menu()
        )

# Admin questions menu
async def admin_questions_menu(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    await safe_edit_message_text(update, 
        "❓ Question Management\n\nChoose an action:",
        reply_markup=get_admin_questions_menu()
    )

# Add question
async def admin_add_question_start(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    await safe_edit_message_text(update, 
        "➕ Add New Question\n\nPlease provide the question in the following format:\n\n"
        "**Question Text**\n"
        "Option A: [option A text]\n"
        "Option B: [option B text]\n"
        "Option C: [option C text]\n"
        "Option D: [option D text]\n"
        "Correct: [A/B/C/D]\n"
        "Course: [course name]\n"
        "Difficulty: [easy/medium/hard]"
    )

# Edit question
async def admin_edit_question_start(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    await safe_edit_message_text(update, 
        "✏️ Edit Question\n\nPlease provide the question ID and the new question details:"
    )

# Delete question
async def admin_delete_question_start(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    db = SessionLocal()
    questions = db.query(Question).all()

    if not questions:
        await safe_edit_message_text(update, 
            "❓ No questions available to delete.",
            reply_markup=get_admin_questions_menu()
        )
        db.close()
        return

    message_text = "🗑️ Select a question to delete:\n\n"
    for question in questions[:10]:  # Limit to first 10 for simplicity
        message_text += f"🆔 ID: {question.id}\n"
        message_text += f"📝 Question: {question.text[:50]}...\n"
        message_text += f"🎯 Course: {question.course or 'Not set'}\n\n"

    await safe_edit_message_text(update, 
        message_text,
        reply_markup=get_admin_questions_menu()
    )
    db.close()

# Confirm delete
async def admin_confirm_delete(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    question_id = int(update.callback_query.data.split("_")[-1])
    await safe_edit_message_text(update, 
        f"⚠️ Confirm Deletion\n\nAre you sure you want to delete question {question_id}?",
        reply_markup=get_admin_confirm_delete(question_id)
    )

# Handle admin text input
async def handle_admin_text_input(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        return

    text = update.message.text.strip()
    
    # Parse different types of admin input
    if "add_question" in context.user_data:
        try:
            # Parse question format
            lines = text.split('\n')
            if len(lines) >= 8:
                question_text = lines[0]
                options = {}
                correct_option = ""
                course = ""
                difficulty = ""

                for line in lines[1:]:
                    if line.startswith("Option A:"):
                        options['A'] = line.replace("Option A: ", "").strip()
                    elif line.startswith("Option B:"):
                        options['B'] = line.replace("Option B: ", "").strip()
                    elif line.startswith("Option C:"):
                        options['C'] = line.replace("Option C: ", "").strip()
                    elif line.startswith("Option D:"):
                        options['D'] = line.replace("Option D: ", "").strip()
                    elif line.startswith("Correct:"):
                        correct_option = line.replace("Correct: ", "").strip()
                    elif line.startswith("Course:"):
                        course = line.replace("Course: ", "").strip()
                    elif line.startswith("Difficulty:"):
                        difficulty = line.replace("Difficulty: ", "").strip()

                if len(options) == 4 and correct_option in ['A', 'B', 'C', 'D']:
                    # Get exam_id from user data or use default
                    exam_id = context.user_data.get("selected_exam_id", 1)  # Default to Biology Final
                    
                    db = SessionLocal()
                    question = Question(
                        exam_id=exam_id,
                        text=question_text,
                        option_a=options['A'],
                        option_b=options['B'],
                        option_c=options['C'],
                        option_d=options['D'],
                        correct_answer=correct_option,
                        course=course,
                        difficulty=difficulty
                    )
                    db.add(question)
                    db.commit()
                    db.close()

                    await update.message.reply_text(
                        f"✅ Question added successfully to exam ID: {exam_id}!",
                        reply_markup=get_admin_questions_menu()
                    )
                    context.user_data.pop("add_question", None)
                    context.user_data.pop("selected_exam_id", None)
                else:
                    await update.message.reply_text(
                        "❌ Invalid question format. Please try again."
                    )
            else:
                await update.message.reply_text(
                    "❌ Incomplete question format. Please provide all required fields."
                )
        except Exception as e:
            await update.message.reply_text(f"❌ Error adding question: {str(e)}")
    
    elif "edit_question" in context.user_data:
        # Handle question editing
        await update.message.reply_text(
            "✏️ Question editing functionality coming soon!",
            reply_markup=get_admin_questions_menu()
        )
        context.user_data.pop("edit_question", None)
    
    elif "delete_question" in context.user_data:
        try:
            question_id = int(text)
            db = SessionLocal()
            question = db.query(Question).filter_by(id=question_id).first()
            
            if question:
                db.delete(question)
                db.commit()
                db.close()
                await update.message.reply_text(
                    f"✅ Question {question_id} deleted successfully!",
                    reply_markup=get_admin_questions_menu()
                )
            else:
                await update.message.reply_text(
                    f"❌ Question {question_id} not found.",
                    reply_markup=get_admin_questions_menu()
                )
            context.user_data.pop("delete_question", None)
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid question ID. Please provide a number."
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error deleting question: {str(e)}")

# Add question handler
async def admin_add_question(update, context):
    context.user_data["add_question"] = True
    await admin_add_question_start(update, context)

# Edit question handler
async def admin_edit_question(update, context):
    context.user_data["edit_question"] = True
    await admin_edit_question_start(update, context)

# Delete question handler
async def admin_delete_question(update, context):
    context.user_data["delete_question"] = True
    await admin_delete_question_start(update, context)

# Edit question
async def edit_question(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Access denied.")
        return

    # Handle question editing
    await update.message.reply_text("Edit question functionality coming soon!")

# Delete question
async def delete_question(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Access denied.")
        return

    # Handle question deletion
    await update.message.reply_text("Delete question functionality coming soon!")

# Back to main menu
async def admin_back_main(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    await admin_panel(update, context)

# View exam results
async def admin_results(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.answer("Access denied.")
            await safe_edit_message_text(update, "Access denied.")
        else:
            await update.message.reply_text("Access denied.")
        return

    db = SessionLocal()
    results = db.query(Exam).all()

    if not results:
        message_text = "📊 Exam Results\n\nNo exam results found."
    else:
        message_text = "📊 Exam Results:\n\n"
        for exam in results:
            message_text += f"🆔 ID: {exam.id}\n"
            message_text += f"📝 Title: {exam.title}\n"
            message_text += f"📊 Total Questions: {exam.total_questions}\n"
            message_text += f"⏱️ Duration: {exam.duration} minutes\n"
            message_text += f"📅 Created: {exam.created_at.strftime('%Y-%m-%d') if exam.created_at else 'Unknown'}\n\n"
            message_text += "➖" * 20 + "\n\n"

    if hasattr(update, 'callback_query') and update.callback_query:
        await safe_edit_message_text(update, 
            message_text,
            reply_markup=get_admin_main_menu()
        )
    else:
        await update.message.reply_text(
            message_text,
            reply_markup=get_admin_main_menu()
        )

    db.close()

# Export menu
async def admin_export_menu(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    await safe_edit_message_text(update, 
        "📈 Export Results\n\nChoose export format:",
        reply_markup=get_admin_export_menu()
    )

# Export CSV
async def admin_export_csv(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    await safe_edit_message_text(update, 
        "📄 CSV Export\n\nGenerating CSV file...",
        reply_markup=get_admin_export_menu()
    )

# Export Excel
async def admin_export_excel(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.callback_query.answer("Access denied.")
        return

    await safe_edit_message_text(update, 
        "📊 Excel Export\n\nGenerating Excel file...",
        reply_markup=get_admin_export_menu()
    )

# Command handlers for admin functions
async def approve(update, context):
    """Admin command to approve a payment"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Access denied.")
        return

    try:
        payment_id = int(update.message.text.split('_')[1])
        success = approve_payment(payment_id)
        
        if success:
            await update.message.reply_text(f"✅ Payment {payment_id} approved successfully!")
        else:
            await update.message.reply_text(f"❌ Payment {payment_id} not found.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Invalid payment ID. Use /approve_<payment_id>")

async def reject(update, context):
    """Admin command to reject a payment"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Access denied.")
        return

    try:
        payment_id = int(update.message.text.split('_')[1])
        success = reject_payment(payment_id)
        
        if success:
            await update.message.reply_text(f"❌ Payment {payment_id} rejected.")
        else:
            await update.message.reply_text(f"❌ Payment {payment_id} not found.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Invalid payment ID. Use /reject_<payment_id>")

async def exam_analytics(update, context):
    """Show exam analytics"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Access denied.")
        return

    await update.message.reply_text("📊 Exam analytics functionality coming soon!")
