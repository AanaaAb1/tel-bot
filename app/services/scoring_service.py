from app.database.session import SessionLocal
from app.models.answer import Answer
from app.models.result import Result
from app.models.question import Question

PASS_PERCENTAGE = 70  # >=70% is pass

def finalize_exam(user_id, exam_id):
    db = SessionLocal()

    answers = db.query(Answer).filter_by(user_id=user_id).filter(Answer.question_id.in_(
        db.query(Question.id).filter_by(exam_id=exam_id)
    )).all()

    correct_answers = sum(1 for a in answers if a.is_correct)
    total_questions = len(answers)
    wrong_answers = total_questions - correct_answers
    percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0

    result = Result(
        user_id=user_id,
        exam_id=exam_id,
        score=correct_answers,
        percentage=percentage
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    db.close()

    return {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "percentage": percentage,
        "passed": percentage >= PASS_PERCENTAGE,
        "result_id": result.id
    }

def get_detailed_feedback(user_id, exam_id):
    """Get detailed feedback showing each question and user's answer"""
    db = SessionLocal()

    answers = db.query(Answer).join(Question).filter(
        Answer.user_id == user_id,
        Question.exam_id == exam_id
    ).all()

    feedback = []
    for answer in answers:
        question = answer.question
        feedback.append({
            "question_text": question.text[:100] + "..." if len(question.text) > 100 else question.text,
            "user_answer": answer.selected_option,
            "correct_answer": question.correct_answer,
            "is_correct": answer.is_correct
        })

    db.close()
    return feedback