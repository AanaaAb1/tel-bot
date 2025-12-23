from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from app.services.question_service import is_true_false_question

def question_keyboard(question):
    """Create keyboard based on question type"""
    if is_true_false_question(question):
        # True/False question
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("TRUE", callback_data="ans_TRUE")],
            [InlineKeyboardButton("FALSE", callback_data="ans_FALSE")],
        ])
    else:
        # Multiple choice question
        buttons = []
        if question.option_a:
            buttons.append([InlineKeyboardButton("A", callback_data="ans_A")])
        if question.option_b:
            buttons.append([InlineKeyboardButton("B", callback_data="ans_B")])
        if question.option_c:
            buttons.append([InlineKeyboardButton("C", callback_data="ans_C")])
        if question.option_d:
            buttons.append([InlineKeyboardButton("D", callback_data="ans_D")])

        return InlineKeyboardMarkup(buttons)

def format_question_text(question):
    """Format question text with options"""
    text = question.text + "\n\n"

    if is_true_false_question(question):
        text += "TRUE or FALSE?"
    else:
        if question.option_a:
            text += f"A) {question.option_a}\n"
        if question.option_b:
            text += f"B) {question.option_b}\n"
        if question.option_c:
            text += f"C) {question.option_c}\n"
        if question.option_d:
            text += f"D) {question.option_d}\n"

    return text

def exam_selection_keyboard(course_id):
    """Create keyboard for selecting exams/chapters for practice"""
    from app.database.session import SessionLocal
    from app.models.exam import Exam

    db = SessionLocal()
    exams = db.query(Exam).filter_by(course_id=course_id).all()
    db.close()

    buttons = [
        [InlineKeyboardButton(exam.name, callback_data=f"practice_chapter_{exam.id}")]
        for exam in exams
    ]

    # Add back button
    buttons.append([InlineKeyboardButton("⬅️ Back to Courses", callback_data="practice_course")])

    return InlineKeyboardMarkup(buttons)