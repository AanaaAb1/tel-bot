import csv
import sys
import os
from sqlalchemy import inspect

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models import Course, Chapter, Question

def create_database_tables():
    """Create all database tables if they don't exist"""
    from app.database.base import Base
    from app.database.session import engine
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def import_questions():
    db = SessionLocal()
    
    try:
        # Create tables first
        create_database_tables()
        
        questions_imported = 0
        courses_created = 0
        chapters_created = 0
        
        print("Starting question import from questions.csv...")
        
        with open("questions.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            print(f"CSV columns: {reader.fieldnames}")
            
            for row_num, row in enumerate(reader, start=2):  # Start from 2 because of header
                try:
                    print(f"Processing row {row_num}: {row['course']} - {row['chapter']}")
                    
                    # Add course if not exists
                    course = db.query(Course).filter_by(name=row['course']).first()
                    if not course:
                        course = Course(name=row['course'])
                        db.add(course)
                        db.commit()
                        courses_created += 1
                        print(f"  Created course: {row['course']}")
                    
                    # Add chapter if not exists
                    chapter = db.query(Chapter).filter_by(course_id=course.id, name=row['chapter']).first()
                    if not chapter:
                        chapter = Chapter(course_id=course.id, name=row['chapter'])
                        db.add(chapter)
                        db.commit()
                        chapters_created += 1
                        print(f"  Created chapter: {row['chapter']}")
                    
                    # Add question with proper field mapping
                    question = Question(
                        chapter_id=chapter.id,
                        text=row['question_text'],  # CSV field 'question_text' maps to DB field 'text'
                        option_a=row['option_a'],
                        option_b=row['option_b'],
                        option_c=row['option_c'],
                        option_d=row['option_d'],
                        correct_answer=row['correct_option'],  # CSV field 'correct_option' maps to DB field 'correct_answer'
                        course=row['course'],  # Keep for backward compatibility
                        explanation=row['explanation']  # Add explanation field
                    )
                    db.add(question)
                    questions_imported += 1
                    print(f"  Added question {questions_imported}: {row['question_text'][:50]}...")
                    
                except Exception as e:
                    print(f"Error processing row {row_num}: {e}")
                    db.rollback()
                    continue
        
        # Commit all questions
        db.commit()
        print(f"\nImport completed successfully!")
        print(f"Courses created: {courses_created}")
        print(f"Chapters created: {chapters_created}")
        print(f"Questions imported: {questions_imported}")
        
        # Verify import
        total_courses = db.query(Course).count()
        total_chapters = db.query(Chapter).count()
        total_questions = db.query(Question).count()
        
        print(f"\nDatabase verification:")
        print(f"Total courses in database: {total_courses}")
        print(f"Total chapters in database: {total_chapters}")
        print(f"Total questions in database: {total_questions}")
        
        # Show sample questions
        print(f"\nSample questions from database:")
        sample_questions = db.query(Question).limit(3).all()
        for q in sample_questions:
            print(f"  - {q.text[:60]}... (Answer: {q.correct_answer})")
            
    except Exception as e:
        print(f"Fatal error during import: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_questions()
