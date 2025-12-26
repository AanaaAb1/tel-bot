from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_admin_main_menu():
    """Main admin panel menu - 2-column layout"""
    keyboard = [
        # Row 1: Users + Payments
        [InlineKeyboardButton("👥 View All Users", callback_data="admin_users"),
         InlineKeyboardButton("💰 Approve/Reject Payments", callback_data="admin_payments")],
        # Row 2: Add Exam + Manage Questions
        [InlineKeyboardButton("📝 Add Exam", callback_data="admin_add_exam"),
         InlineKeyboardButton("❓ Manage Questions", callback_data="admin_questions")],
        # Row 3: View Results + Export
        [InlineKeyboardButton("📊 View Exam Results", callback_data="admin_results"),
         InlineKeyboardButton("📈 Export Results", callback_data="admin_export")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_questions_menu():
    """Enhanced Questions management menu with course selection - 2-column layout"""
    keyboard = [
        # Row 1: Add Question + Edit Question (Enhanced)
        [InlineKeyboardButton("➕ Add Question", callback_data="admin_select_course"),
         InlineKeyboardButton("✏️ Edit Question", callback_data="admin_edit_question")],
        # Row 2: Delete Question + Back to Main
        [InlineKeyboardButton("🗑️ Delete Question", callback_data="admin_delete_question"),
         InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="admin_back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_export_menu():
    """Export results menu - 2-column layout"""
    keyboard = [
        # Row 1: CSV Export + Excel Export
        [InlineKeyboardButton("📄 Export as CSV", callback_data="admin_export_csv"),
         InlineKeyboardButton("📊 Export as Excel", callback_data="admin_export_excel")],
        # Row 2: Back to Main Menu (spans both columns)
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="admin_back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_confirm_delete(question_id):
    """Confirmation for question deletion"""
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Delete", callback_data=f"admin_confirm_delete_{question_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_questions")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_approval_keyboard(payment_id):
    """Inline keyboard for approving/rejecting payments"""
    keyboard = [
        [InlineKeyboardButton("✅ Approve Payment", callback_data=f"approve_payment_{payment_id}")],
        [InlineKeyboardButton("❌ Reject Payment", callback_data=f"reject_payment_{payment_id}")],
        [InlineKeyboardButton("⬅️ Back to Payments", callback_data="admin_payments")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_course_selection_keyboard(courses):
    """Course selection keyboard for exam creation"""
    keyboard = []
    for course in courses:
        keyboard.append([InlineKeyboardButton(
            f"📚 {course.name}", 
            callback_data=f"select_course_for_exam_{course.id}"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back to Admin Menu", callback_data="admin_back_main")])
    return InlineKeyboardMarkup(keyboard)
