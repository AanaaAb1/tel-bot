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

def get_course_by_name(name):
    """Get course by name"""
    db = SessionLocal()
    course = db.query(Course).filter_by(name=name).first()
    db.close()
    return course

def get_courses_by_code(course_code):
    """Get course by code (like 'maths', 'physics', 'bio', etc.)"""
    db = SessionLocal()
    # Map course codes to actual course names
    code_to_name = {
        'maths': 'Mathematics',
        'physics': 'Physics', 
        'chemistry': 'Chemistry',
        'biology': 'Biology',
        'english': 'English',
        'bio': 'Biology',  # Alternative code for Biology
        'geography': 'Geography',  # Geography now exists in database
        'history': 'History',  # History now exists in database
        # These don't exist in database but might be clicked
        'government': None,
        'economics': None,
        'literature': None
    }
    
    course_name = code_to_name.get(course_code.lower())
    if not course_name:
        db.close()
        return []
    
    # If course_name is None, it means the course doesn't exist in database
    if course_name is None:
        db.close()
        return []
    
    courses = db.query(Course).filter(Course.name.ilike(f'%{course_name}%')).all()
    db.close()
    return courses
