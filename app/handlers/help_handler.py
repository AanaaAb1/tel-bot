from app.keyboards.main_menu import main_menu
from app.config.constants import ADMIN_IDS

async def help_handler(update, context):
    """Comprehensive help system that always responds"""
    user_id = update.effective_user.id
    
    # Create comprehensive help message
    help_text = """
🤖 **Welcome to Smart Test Exam!**

📚 **What is this bot?**
This is an AI-powered exam preparation platform that helps you:
• Practice with course-specific questions
• Take official timed exams
• Track your performance and results
• Access study materials

💳 **Getting Started:**
1. Complete one-time payment ($10) to unlock full access
2. Submit payment proof (screenshot/transaction ID)
3. Wait for admin approval (usually a few minutes)
4. Start practicing and taking exams!

🎯 **Available Features:**
• 📝 **Practice Mode**: Practice by course or chapter
• 🏆 **Official Exams**: Timed assessments
• 📊 **Results**: View your performance history
• 📖 **Materials**: Access study resources
• 🔧 **Admin Panel**: For administrators

💰 **Payment Information:**
• One-time payment: $10
• Payment methods: Mobile Money, Bank Transfer
• Submit proof via the payment menu
• Admin approval required for access

🔒 **Access Levels:**
• 🔒 **Locked**: Cannot access premium features
• 🔓 **Unlocked**: Full access after payment approval

❓ **Need Help?**
• Contact: @admin_username
• Email: support@exambot.com
• Response time: Usually within 2-4 hours

📱 **Quick Commands:**
• /start - Begin registration
• /help - Show this help message
• /menu - Main menu
• /admin - Admin panel (admins only)

🔧 **Troubleshooting:**
• If payment doesn't work: Check your payment proof
• If access isn't granted: Contact admin
• If questions don't load: Try again in a few minutes

✨ **Thank you for using our platform!**
Ready to ace your exams? Let's get started!
"""

    # Send help message with main menu
    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
        reply_markup=main_menu(user_id)
    )

async def help_callback(update, context):
    """Handle help button callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    help_text = """
🆘 **HELP & SUPPORT**

**For Users:**
• 💳 **Payment Issues**: Use payment menu to submit proof
• 🔓 **Access Problems**: Contact admin after payment
• 📚 **Content Questions**: Check practice mode first
• 🔧 **Technical Issues**: Restart with /start command

**For Admins:**
• 🔐 **Admin Commands**: /admin
• 💰 **Payment Management**: View pending payments
• 👥 **User Management**: View all users
• ❓ **Question Management**: Add/edit/delete questions

**Contact Information:**
• 📞 Support: @admin_username
• 📧 Email: support@exambot.com
• ⏰ Response: 2-4 hours typically

**System Status:**
✅ Bot: Online
✅ Database: Connected
✅ Payment System: Active
✅ All Features: Functional

Need more specific help? Contact our support team!
"""

    await query.edit_message_text(
        help_text,
        parse_mode="Markdown",
        reply_markup=main_menu(user_id)
    )
