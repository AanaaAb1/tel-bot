from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.session import SessionLocal
from app.models.course import Course

def course_keyboard():
    db = SessionLocal()
    courses = db.query(Course).all()
    db.close()

    buttons = [
        [InlineKeyboardButton(c.name, callback_data=f"exam_course_{c.id}")]
        for c in courses
    ]

    return InlineKeyboardMarkup(buttons)