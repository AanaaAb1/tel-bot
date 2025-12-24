"""
Constants for the Smart Test Exam
"""
import os

# Admin User IDs
# Set this in your .env file as comma-separated values: ADMIN_USER_IDS=123456789,987654321
ADMIN_IDS = [5642507992, 7342121804]
admin_env = os.getenv('ADMIN_USER_IDS', '')
if admin_env:
    try:
        env_admin_ids = [int(uid.strip()) for uid in admin_env.split(',') if uid.strip()]
        ADMIN_IDS.extend(env_admin_ids)  # Add environment admin IDs to the list
    except ValueError:
        print("Warning: Invalid ADMIN_USER_IDS format. Expected comma-separated integers.")

# Payment Status Constants
PAYMENT_PENDING = "pending"
PAYMENT_APPROVED = "approved"
PAYMENT_REJECTED = "rejected"
PAYMENT_COMPLETED = "completed"

# Payment status options for keyboards and validation
PAYMENT_STATUSES = [
    PAYMENT_PENDING,
    PAYMENT_APPROVED, 
    PAYMENT_REJECTED,
    PAYMENT_COMPLETED
]

# Access Control Constants
ACCESS_LOCKED = "locked"
ACCESS_UNLOCKED = "unlocked"

ACCESS_STATUSES = [
    ACCESS_LOCKED,
    ACCESS_UNLOCKED
]

# User Level Constants
LEVEL_FRESHMAN = "freshman"
LEVEL_REMEDIAL = "remedial"

USER_LEVELS = [
    LEVEL_FRESHMAN,
    LEVEL_REMEDIAL
]

# Stream Constants  
STREAM_NATURAL_SOCIAL = "natural_social"
STREAM_SCIENCE = "science"
STREAM_ARTS = "arts"
STREAM_COMMERCE = "commerce"

STREAMS = [
    STREAM_NATURAL_SOCIAL,
    STREAM_SCIENCE,
    STREAM_ARTS,
    STREAM_COMMERCE
]

# Course Types
COURSE_PRACTICE = "practice"
COURSE_EXAM = "exam"
COURSE_MOCK = "mock"

COURSE_TYPES = [
    COURSE_PRACTICE,
    COURSE_EXAM,
    COURSE_MOCK
]

# Question Types
QUESTION_MULTIPLE_CHOICE = "multiple_choice"
QUESTION_TRUE_FALSE = "true_false"
QUESTION_SHORT_ANSWER = "short_answer"

QUESTION_TYPES = [
    QUESTION_MULTIPLE_CHOICE,
    QUESTION_TRUE_FALSE,
    QUESTION_SHORT_ANSWER
]

# Bot Commands
COMMAND_START = "/start"
COMMAND_HELP = "/help"
COMMAND_REGISTER = "/register"
COMMAND_MENU = "/menu"
COMMAND_PAYMENT = "/payment"
COMMAND_ADMIN = "/admin"

# Callback Data Prefixes
CALLBACK_PAYMENT_APPROVE = "payment_approve"
CALLBACK_PAYMENT_REJECT = "payment_reject"
CALLBACK_COURSE_SELECT = "course_select"
CALLBACK_LEVEL_SELECT = "level_select"
CALLBACK_STREAM_SELECT = "stream_select"
CALLBACK_QUESTION_ANSWER = "question_answer"
CALLBACK_EXAM_START = "exam_start"
CALLBACK_EXAM_NEXT = "exam_next"
CALLBACK_EXAM_FINISH = "exam_finish"

# Keyboard Button Texts
BUTTON_PAYMENT = "💳 Payment"
BUTTON_COURSES = "📚 Courses"
BUTTON_EXAMS = "📝 Exams"
BUTTON_PRACTICE = "🎯 Practice"
BUTTON_PROFILE = "👤 Profile"
BUTTON_LEADERBOARD = "🏆 Leaderboard"
BUTTON_HELP = "❓ Help"
BUTTON_BACK = "⬅️ Back"
BUTTON_MAIN_MENU = "🏠 Main Menu"

# Payment Provider Constants
PAYMENT_PROVIDER = "telegram"  # telegram, stripe, paypal, etc.

# Database Table Names
TABLE_USERS = "users"
TABLE_PAYMENTS = "payments"
TABLE_COURSES = "courses"
TABLE_QUESTIONS = "questions"
TABLE_EXAMS = "exams"
TABLE_ANSWERS = "answers"
TABLE_RESULTS = "results"

# Message Texts
WELCOME_MESSAGE = """
🎓 Welcome to Smart Test Exam!

This intelligent bot will help you:
• Take practice tests
• Prepare for exams
• Track your progress
• Access personalized learning

Click /register to sign up or /menu to access features.
"""

HELP_MESSAGE = """
🤖 Smart Test Exam - Help

Available commands:
/start - Start using the bot
/register - User registration
/menu - Main menu
/payment - Pay subscription
/help - Show this help

You need to pay for a subscription to access courses and exams.
"""

ADMIN_HELP_MESSAGE = """
👑 Admin Panel

Available functions:
• View users
• Manage payments
• Create courses and questions
• View statistics

Use the menu buttons for navigation.
"""

# Error Messages
ERROR_NO_ACCESS = "❌ You don't have access to this feature. Contact an administrator."
ERROR_NOT_REGISTERED = "❌ You are not registered. Use /register to register."
ERROR_NO_PAYMENT = "❌ You need to pay for a subscription to access this feature."
ERROR_INVALID_INPUT = "❌ Invalid input. Please try again."
ERROR_DATABASE = "❌ Database error. Please try again later."

# Success Messages
SUCCESS_REGISTERED = "✅ Registration completed successfully!"
SUCCESS_PAYMENT_APPROVED = "✅ Payment approved!"
SUCCESS_PAYMENT_REJECTED = "❌ Payment rejected!"
SUCCESS_COURSE_CREATED = "✅ Course created!"
SUCCESS_QUESTION_ADDED = "✅ Question added!"

print(f"✅ Constants loaded successfully")
print(f"👥 Admin IDs: {ADMIN_IDS}")
print(f"💰 Payment statuses: {PAYMENT_STATUSES}")
print(f"📚 User levels: {USER_LEVELS}")
