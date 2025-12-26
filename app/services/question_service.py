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

def get_questions_by_chapter(chapter_id, limit=None):
    """Get random questions from a specific chapter"""
    db = SessionLocal()
    questions = db.query(Question).filter_by(chapter_id=chapter_id).all()
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

def add_question(exam_id, question_text, option_a, option_b, option_c=None, option_d=None, correct_answer=None, course=None, chapter_id=None, difficulty='medium'):
    """Add a new question to an exam with enhanced course/chapter support"""
    db = SessionLocal()
    try:
        question = Question(
            exam_id=exam_id,
            text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer or 'A',
            course=course,
            chapter_id=chapter_id,
            difficulty=difficulty
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

def add_question_by_course_chapter(course, chapter_name, question_text, option_a, option_b, option_c=None, option_d=None, correct_answer='A', difficulty='medium'):
    """Add question by course and chapter name (convenience method)"""
    from app.models.chapter import Chapter
    from app.models.course import Course
    from app.models.exam import Exam
    
    db = SessionLocal()
    try:
        # Find the course
        course_obj = db.query(Course).filter(Course.name == course).first()
        if not course_obj:
            raise ValueError(f"Course '{course}' not found")
        
        # Find the chapter/exam
        chapter_obj = db.query(Chapter).filter(
            Chapter.name == chapter_name,
            Chapter.course_id == course_obj.id
        ).first()
        
        if not chapter_obj:
            raise ValueError(f"Chapter '{chapter_name}' not found in course '{course}'")
        
        # Find an exam for this course
        exam_obj = db.query(Exam).filter(Exam.course_id == course_obj.id).first()
        if not exam_obj:
            # If no exam exists, create a default one
            exam_obj = Exam(
                course_id=course_obj.id,
                name=f"{course_obj.name} Exam",
                total_questions=0
            )
            db.add(exam_obj)
            db.commit()
            db.refresh(exam_obj)
        
        # Create question with proper mapping
        question = Question(
            text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            course=course,
            chapter_id=chapter_obj.id,
            exam_id=exam_obj.id,
            difficulty=difficulty
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
            "correct_answer": q.correct_answer
        })
    db.close()
    return result

# Enhanced retrieval methods for course/chapter organization
def get_questions_by_course_chapter(course_name, chapter_name, limit=None):
    """Get questions for a specific course and chapter"""
    from app.models.chapter import Chapter
    from app.models.course import Course
    
    db = SessionLocal()
    try:
        # Find the course and chapter
        course_obj = db.query(Course).filter(Course.name == course_name).first()
        if not course_obj:
            return []
            
        chapter_obj = db.query(Chapter).filter(
            Chapter.name == chapter_name,
            Chapter.course_id == course_obj.id
        ).first()
        
        if not chapter_obj:
            return []
        
        # Get questions for this chapter
        questions = db.query(Question).filter(
            Question.chapter_id == chapter_obj.id
        ).all()
        
        random.shuffle(questions)
        if limit:
            return questions[:limit]
        return questions
        
    except Exception as e:
        print(f"Error getting questions by course/chapter: {e}")
        return []
    finally:
        db.close()

def get_questions_by_course_name(course_name, limit=None):
    """Get all questions for a course (across all chapters)"""
    db = SessionLocal()
    try:
        questions = db.query(Question).filter(Question.course == course_name).all()
        random.shuffle(questions)
        if limit:
            return questions[:limit]
        return questions
    except Exception as e:
        print(f"Error getting questions by course name: {e}")
        return []
    finally:
        db.close()

def get_questions_with_fallback(course_name, chapter_name=None, limit=10):
    """Get questions with intelligent fallback:
    1. Try to get questions for specific course + chapter
    2. If no chapter questions, get course-wide questions
    3. If no course questions, return empty list
    """
    # First try: specific chapter
    if chapter_name:
        chapter_questions = get_questions_by_course_chapter(course_name, chapter_name, limit=limit)
        if chapter_questions:
            return chapter_questions
    
    # Second try: course-wide questions
    course_questions = get_questions_by_course_name(course_name, limit=limit)
    if course_questions:
        return course_questions
    
    # No questions found
    return []

def get_chapter_question_count(course_name, chapter_name):
    """Get count of questions for a specific chapter"""
    from app.models.chapter import Chapter
    from app.models.course import Course
    
    db = SessionLocal()
    try:
        course_obj = db.query(Course).filter(Course.name == course_name).first()
        if not course_obj:
            return 0
            
        chapter_obj = db.query(Chapter).filter(
            Chapter.name == chapter_name,
            Chapter.course_id == course_obj.id
        ).first()
        
        if not chapter_obj:
            return 0
        
        count = db.query(Question).filter(Question.chapter_id == chapter_obj.id).count()
        return count
        
    except Exception as e:
        print(f"Error getting chapter question count: {e}")
        return 0
    finally:
        db.close()

def get_course_question_count(course_name):
    """Get total count of questions for a course"""
    db = SessionLocal()
    try:
        count = db.query(Question).filter(Question.course == course_name).count()
        return count
    except Exception as e:
        print(f"Error getting course question count: {e}")
        return 0
    finally:
        db.close()

def get_questions_summary():
    """Get summary of questions by course and chapter"""
    from app.models.chapter import Chapter
    from app.models.course import Course
    
    db = SessionLocal()
    try:
        # Get all courses with question counts
        courses = db.query(Course).all()
        summary = []
        
        for course in courses:
            chapters = db.query(Chapter).filter(Chapter.course_id == course.id).all()
            course_questions = db.query(Question).filter(Question.course == course.name).count()
            
            chapter_info = []
            for chapter in chapters:
                chapter_questions = db.query(Question).filter(Question.chapter_id == chapter.id).count()
                chapter_info.append({
                    "name": chapter.name,
                    "question_count": chapter_questions
                })
            
            summary.append({
                "course_name": course.name,
                "total_questions": course_questions,
                "chapters": chapter_info
            })
        
        return summary
        
    except Exception as e:
        print(f"Error getting questions summary: {e}")
        return []
    finally:
        db.close()
