from app.database.session import SessionLocal
from app.models.course import Course

def get_all_courses():
    """Get all available courses"""
    db = SessionLocal()
    courses = db.query(Course).all()
    db.close()
    return courses

def get_course_by_id(course_id):
    """Get a specific course by ID"""
    db = SessionLocal()
    course = db.query(Course).filter_by(id=course_id).first()
    db.close()
    return course