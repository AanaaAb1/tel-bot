from app.database.session import SessionLocal
from app.models.user import User
from app.keyboards.payment_keyboard import payment_keyboard
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def check_user_payment_access(user):
    """Check user payment status and return access status"""
    if not user:
        return False, "USER_NOT_FOUND"
    
    payment_status = user.payment_status
    
    if payment_status in ["APPROVED", "APPROVED"]:
        return True, "APPROVED"
    elif payment_status in ["NEW", "NOT_PAID"]:
        return False, "NOT_PAID"
    elif payment_status == "PENDING_PAYMENT":
        return False, "PENDING_PAYMENT" 
    elif payment_status == "PAYMENT_REJECTED":
        return False, "PAYMENT_REJECTED"
    else:
        return False, "UNKNOWN"

async def enforce_payment_access(update, context):
    """Enforce payment access control for exams"""
    query = update.callback_query
    user_id = query.from_user.id
    
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    db.close()
    
    has_access, status = check_user_payment_access(user)
    
    if not has_access:
        if status == "NOT_PAID":
            await query.edit_message_text(
                "⚠️ **Access Restricted**\n\n"
                "You must complete payment to access exams.\n\n"
                "Please proceed to payment and wait for admin approval.",
                reply_markup=payment_keyboard(),
                parse_mode="Markdown"
            )
        elif status == "PENDING_PAYMENT":
            await query.edit_message_text(
                "⏳ **Payment Under Review**\n\n"
                "Your payment is awaiting admin approval.\n"
                "You will be notified once approved.",
                reply_markup=payment_keyboard(),
                parse_mode="Markdown"
            )
        elif status == "PAYMENT_REJECTED":
            await query.edit_message_text(
                "❌ **Payment Rejected**\n\n"
                "Please resubmit valid payment proof to gain access.",
                reply_markup=payment_keyboard(),
                parse_mode="Markdown"
            )
        elif status == "USER_NOT_FOUND":
            await query.edit_message_text(
                "⚠️ **Account Not Found**\n\n"
                "Please register first before accessing exams.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Register", callback_data="register")]])
            )
        else:
            await query.edit_message_text(
                "⚠️ **Access Denied**\n\n"
                "Please contact admin for assistance.",
                reply_markup=payment_keyboard()
            )
        return False
    
    return True

def check_course_access(user, course_name):
    """Check if user has access to a specific course based on their stream AND level"""
    if not user:
        return False

    # Check stream-based access first
    stream_access = False
    if user.stream:
        stream_courses = {
            "natural_science": ["Biology", "Physics", "Chemistry", "Mathematics", "English"],
            "social_science": ["History", "Geography", "Government", "Economics", "Literature", "Mathematics", "English"]
        }

        user_stream = user.stream.lower()
        if user_stream in stream_courses:
            if course_name in stream_courses[user_stream]:
                stream_access = True

    # Check level-based access
    level_access = False
    if user.level:
        user_level = user.level.lower()
        
        # Define level-based course access - COMMON + STREAM SPECIFIC
        level_courses = {
            "remedial": {
                "natural_science": ["Mathematics", "English", "Biology", "Physics", "Chemistry"],  # Natural Science remedial: common + science
                "social_science": ["Mathematics", "English", "History", "Geography"]  # Social Science remedial: common + social studies
            },
            "freshman": {
                "natural_science": ["Mathematics", "English", "Biology", "Physics", "Chemistry"],  # Natural Science all courses
                "social_science": ["Mathematics", "English", "History", "Geography", "Government", "Economics", "Literature"]  # Social Science all courses
            }
        }
        
        if user_level in level_courses and user.stream:
            user_stream_lower = user.stream.lower()
            if user_stream_lower in level_courses[user_level]:
                level_access = course_name in level_courses[user_level][user_stream_lower]

    # User must have BOTH stream access AND level access
    return stream_access and level_access

def check_level_access(user, required_level):
    """Check if user has access to a specific level content"""
    if not user or not user.level:
        return False

    user_level = user.level.lower()
    required_level = required_level.lower()

    # Define level hierarchy: remedial < freshman
    level_hierarchy = {
        "remedial": 1,
        "freshman": 2
    }

    user_level_num = level_hierarchy.get(user_level, 0)
    required_level_num = level_hierarchy.get(required_level, 999)

    # Users can access their level and below
    return user_level_num >= required_level_num

def get_user_accessible_levels(user):
    """Get list of levels user can access based on their level"""
    if not user or not user.level:
        return []

    user_level = user.level.lower()
    
    # Define level hierarchy
    level_hierarchy = ["remedial", "freshman"]
    
    if user_level in level_hierarchy:
        user_index = level_hierarchy.index(user_level)
        return level_hierarchy[:user_index + 1]  # Return current level and below
    
    return []

def get_access_status_message(user):
    """Get appropriate message based on user payment status"""
    if not user:
        return "⚠️ Account not found. Please register first."
    
    payment_status = user.payment_status
    
    if payment_status == "APPROVED":
        return f"✅ **Account Status:** Approved\n\nYou have full access to all exams and features!"
    elif payment_status in ["NEW", "NOT_PAID"]:
        return "⚠️ **Access Restricted**\n\nYou must complete payment to access exams. Please proceed to payment and wait for admin approval."
    elif payment_status == "PENDING_PAYMENT":
        return "⏳ **Payment Under Review**\n\nYour payment is awaiting admin approval. You will be notified once approved."
    elif payment_status == "PAYMENT_REJECTED":
        return "❌ **Payment Rejected**\n\nPlease resubmit valid payment proof to gain access."
    else:
        return "⚠️ **Unknown Status**\n\nPlease contact admin for assistance."
