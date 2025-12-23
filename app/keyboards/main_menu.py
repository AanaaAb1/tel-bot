from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from app.config.constants import ADMIN_IDS

def main_menu(user_id=None):
    buttons = [
        [InlineKeyboardButton("👤 Profile", callback_data="profile"), InlineKeyboardButton("📘 Courses", callback_data="courses")],
        [InlineKeyboardButton("🎯 Practice", callback_data="practice"), InlineKeyboardButton("📝 Exams", callback_data="exams")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"), InlineKeyboardButton("👥 Community", callback_data="community")],
        [InlineKeyboardButton("📚 Materials", callback_data="materials"), InlineKeyboardButton("💳 Payment", callback_data="payment")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]

    if user_id and user_id in ADMIN_IDS:
        buttons.append([InlineKeyboardButton("👑 Admin", callback_data="admin")])

    return InlineKeyboardMarkup(buttons)
