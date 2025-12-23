import random
from app.database.session import SessionLocal
from app.models.question import Question
from app.models.exam import Exam

def get_random_questions(exam_id, limit=5):
    """Get random questions for a specific exam"""
    db = SessionLocal()
    questions = db.query(Question).filter_by(exam_id=exam_id).all()
    db.close()

    random.shuffle(questions)
    return questions[:limit]

def get_questions_by_course(course_id, limit=None):
    """Get random questions from all exams in a course"""
    db = SessionLocal()
    questions = db.query(Question).join(Exam).filter(Exam.course_id == course_id).all()
    db.close()

    random.shuffle(questions)
    if limit:
        return questions[:limit]
    return questions

def get_questions_by_exam(exam_id, limit=None):
    """Get random questions from a specific exam (chapter)"""
    db = SessionLocal()
    questions = db.query(Question).filter_by(exam_id=exam_id).all()
    db.close()

    random.shuffle(questions)
    if limit:
        return questions[:limit]
    return questions

def get_question_types():
    """Get available question types"""
    return ["MULTIPLE_CHOICE", "TRUE_FALSE"]

def is_true_false_question(question):
    """Check if a question is true/false type"""
    # For now, we determine this by checking if only option_a and option_b are used
    return (question.option_a and question.option_b and
            not question.option_c and not question.option_d)

def add_question(exam_id, question_text, option_a, option_b, option_c=None, option_d=None, correct_answer=None):
    """Add a new question to an exam"""
    db = SessionLocal()
    try:
        question = Question(
            exam_id=exam_id,
            text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_answer
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def update_question(question_id, **kwargs):
    """Update an existing question"""
    db = SessionLocal()
    try:
        question = db.query(Question).filter_by(id=question_id).first()
        if not question:
            return None

        for key, value in kwargs.items():
            if hasattr(question, key):
                setattr(question, key, value)

        db.commit()
        db.refresh(question)
        return question
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def delete_question(question_id):
    """Delete a question"""
    db = SessionLocal()
    try:
        question = db.query(Question).filter_by(id=question_id).first()
        if not question:
            return False

        db.delete(question)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_all_questions():
    """Get all questions with exam info"""
    db = SessionLocal()
    questions = db.query(Question).join(Exam).all()
    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "exam_id": q.exam_id,
            "exam_name": q.exam.name if q.exam else "Unknown",
            "question_text": q.text,
            "options": [q.option_a, q.option_b, q.option_c, q.option_d],
            "correct_answer": q.correct_option
        })
    db.close()
    return result