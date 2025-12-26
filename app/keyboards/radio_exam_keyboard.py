from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import PollAnswerHandler
from app.services.question_service import is_true_false_question
import logging

logger = logging.getLogger(__name__)

def create_poll_question(question, question_number, total_questions):
    """Create a poll for the question - FIXED to use correct_answer field"""
    if is_true_false_question(question):
        # True/False poll
        options = ["TRUE", "FALSE"]
        correct_option_id = 0 if question.correct_answer == "TRUE" else 1
    else:
        # Multiple choice poll
        options = []
        correct_option_id = 0
        
        if question.option_a:
            options.append(question.option_a)
            if question.correct_answer == "A":
                correct_option_id = len(options) - 1
        if question.option_b:
            options.append(question.option_b)
            if question.correct_answer == "B":
                correct_option_id = len(options) - 1
        if question.option_c:
            options.append(question.option_c)
            if question.correct_answer == "C":
                correct_option_id = len(options) - 1
        if question.option_d:
            options.append(question.option_d)
            if question.correct_answer == "D":
                correct_option_id = len(options) - 1

    # Add A, B, C, D labels if not already present
    labeled_options = []
    for i, option in enumerate(options):
        if not option.startswith(('A)', 'B)', 'C)', 'D)', 'A.', 'B.', 'C.', 'D.')):
            label = chr(65 + i)  # A, B, C, D
            labeled_options.append(f"{label}) {option}")
        else:
            labeled_options.append(option)

    return {
        "question": f"📝 Question {question_number}/{total_questions}\n\n{question.text}",
        "options": labeled_options,
        "correct_option_id": correct_option_id,
        "question_id": question.id
    }

def create_exam_start_keyboard():
    """Create keyboard to start exam/practice"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Start Exam", callback_data="start_exam")],
        [InlineKeyboardButton("📚 Start Practice", callback_data="start_practice")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main")]
    ])

def create_practice_selection_keyboard(course_id):
    """Create keyboard for selecting practice type"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Practice by Course", callback_data=f"practice_course_{course_id}")],
        [InlineKeyboardButton("📋 Practice by Chapter", callback_data=f"practice_course_chapter_{course_id}")],
        [InlineKeyboardButton("⬅️ Back to Courses", callback_data="courses")]
    ])

def create_chapter_selection_keyboard(exams, course_id):
    """Create keyboard for selecting chapters"""
    buttons = []
    for exam in exams:
        buttons.append([InlineKeyboardButton(exam.name, callback_data=f"practice_chapter_{exam.id}")])
    
    buttons.append([InlineKeyboardButton("⬅️ Back to Course", callback_data=f"practice_course_chapter_{course_id}")])
    return InlineKeyboardMarkup(buttons)

def create_result_keyboard(result_data):
    """Create keyboard for exam results"""
    buttons = [
        [InlineKeyboardButton("📊 View Detailed Results", callback_data=f"view_result_{result_data['result_id']}")],
        [InlineKeyboardButton("🔄 Take Another Exam", callback_data="exams")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ]
    
    return InlineKeyboardMarkup(buttons)

def create_detailed_result_keyboard():
    """Create keyboard for detailed results"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Retake Exam", callback_data="exams")],
        [InlineKeyboardButton("📚 Practice More", callback_data="practice")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ])

