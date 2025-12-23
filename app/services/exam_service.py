from app.database.session import SessionLocal
from app.models.exam import Exam

def get_exams_by_course(course_id):
    db = SessionLocal()
    exams = db.query(Exam).filter_by(course_id=course_id).all()
    db.close()
    return exams