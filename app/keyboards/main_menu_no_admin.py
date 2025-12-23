from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu(user_id=None):
    buttons = [
        [InlineKeyboardButton("👤 Profile", callback_data="profile"), InlineKeyboardButton("📘 Courses", callback_data="courses")],
        [InlineKeyboardButton("🎯 Practice", callback_data="practice"), InlineKeyboardButton("📝 Exams", callback_data="exams")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"), InlineKeyboardButton("📚 Materials", callback_data="materials")],
        [InlineKeyboardButton("💳 Payment", callback_data="payment"), InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]

    return InlineKeyboardMarkup(buttons)
