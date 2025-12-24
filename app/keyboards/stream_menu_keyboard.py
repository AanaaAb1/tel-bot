"""
Stream-Specific Menu Keyboards
Separate dashboard layouts for Natural Science and Social Science streams
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from app.config.constants import ADMIN_IDS

def get_natural_science_dashboard_keyboard(user_id=None):
    """Get Natural Science Stream Dashboard Keyboard"""
    
    keyboard = [
        [InlineKeyboardButton("🧬 Natural Science Exams", callback_data="ns_exams")],
        [InlineKeyboardButton("🎯 Practice", callback_data="ns_practice")],
        [InlineKeyboardButton("📚 Materials", callback_data="ns_materials")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="ns_leaderboard")],
        [InlineKeyboardButton("👤 Profile", callback_data="ns_profile")],
        [InlineKeyboardButton("📊 My Results", callback_data="ns_results")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="ns_back_to_main")]
    ]

    if user_id and user_id in ADMIN_IDS:
        keyboard.insert(-2, [InlineKeyboardButton("👑 Admin", callback_data="admin")])

    return InlineKeyboardMarkup(keyboard)

def get_social_science_dashboard_keyboard(user_id=None):
    """Get Social Science Stream Dashboard Keyboard"""
    
    keyboard = [
        [InlineKeyboardButton("🌍 Social Science Exams", callback_data="ss_exams")],
        [InlineKeyboardButton("🎯 Practice", callback_data="ss_practice")],
        [InlineKeyboardButton("📚 Materials", callback_data="ss_materials")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="ss_leaderboard")],
        [InlineKeyboardButton("👤 Profile", callback_data="ss_profile")],
        [InlineKeyboardButton("📊 My Results", callback_data="ss_results")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="ss_back_to_main")]
    ]

    if user_id and user_id in ADMIN_IDS:
        keyboard.insert(-2, [InlineKeyboardButton("👑 Admin", callback_data="admin")])

    return InlineKeyboardMarkup(keyboard)

def get_natural_science_dashboard_message(user):
    """Get Natural Science Stream Dashboard Message"""
    
    level = user.level if user.level else "Unknown"
    access_status = "✅ Active" if user.access == "ACTIVE" else "🔒 Locked"
    
    message = f"""
🧬 NATURAL SCIENCE STREAM DASHBOARD

👤 User: {user.first_name} {user.last_name or ''}
📚 Level: {level.title()}
🏷️ Stream: Natural Science
🔑 Access: {access_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧬 Available Features:

📝 Exams: Take Natural Science stream exams
🎯 Practice: Practice questions from your subjects
📚 Materials: Access learning materials and resources
🏆 Leaderboard: Compare your performance with peers
👤 Profile: View and edit your profile information
📊 Results: Check your exam history and scores

Select an option below:
    """
    
    return message

def get_social_science_dashboard_message(user):
    """Get Social Science Stream Dashboard Message"""
    
    level = user.level if user.level else "Unknown"
    access_status = "✅ Active" if user.access == "ACTIVE" else "🔒 Locked"
    
    message = f"""
🌍 SOCIAL SCIENCE STREAM DASHBOARD

👤 User: {user.first_name} {user.last_name or ''}
📚 Level: {level.title()}
🏷️ Stream: Social Science
🔑 Access: {access_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌍 Available Features:

📝 Exams: Take Social Science stream exams
🎯 Practice: Practice questions from your subjects
📚 Materials: Access learning materials and resources
🏆 Leaderboard: Compare your performance with peers
👤 Profile: View and edit your profile information
📊 Results: Check your exam history and scores

Select an option below:
    """
    
    return message

def get_stream_dashboard_selection_keyboard():
    """Get keyboard for stream selection (for users who haven't selected a stream yet)"""
    
    keyboard = [
        [InlineKeyboardButton("🧬 Natural Science Dashboard", callback_data="natural_science_dashboard")],
        [InlineKeyboardButton("🌍 Social Science Dashboard", callback_data="social_science_dashboard")],
        [InlineKeyboardButton("📋 Register Again", callback_data="register")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_stream_dashboard_selection_message():
    """Get message for stream dashboard selection"""
    
    message = """
🏫 STREAM DASHBOARD SELECTION

Welcome to your personalized dashboard!

Please select your stream to access your dedicated dashboard:

🧬 NATURAL SCIENCE STREAM
• Biology, Physics, Chemistry
• Mathematics, English
• Science-focused curriculum

🌍 SOCIAL SCIENCE STREAM
• History, Geography, Government
• Economics, Literature
• Humanities-focused curriculum

Select your stream below:
    """
    
    return message
