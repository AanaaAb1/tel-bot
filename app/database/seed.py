import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models import Course, Exam, Question

def seed_database():
    """Seed the database with sample data"""
    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(Course).first():
            print("Database already seeded!")
            return

        print("Seeding database with sample data...")

        # Create courses
        biology = Course(name="Biology", description="Study of living organisms")
        physics = Course(name="Physics", description="Study of matter and energy")
        chemistry = Course(name="Chemistry", description="Study of matter and its transformations")
        english = Course(name="English", description="Study of language and literature")
        maths = Course(name="Maths", description="Study of numbers and mathematical concepts")

        db.add(biology)
        db.add(physics)
        db.add(chemistry)
        db.add(english)
        db.add(maths)
        db.commit()

        # Create exams
        bio_exam = Exam(course_id=biology.id, name="Biology Final", total_questions=10)
        phys_exam = Exam(course_id=physics.id, name="Physics Final", total_questions=10)
        chem_exam = Exam(course_id=chemistry.id, name="Chemistry Final", total_questions=10)
        eng_exam = Exam(course_id=english.id, name="English Final", total_questions=10)
        maths_exam = Exam(course_id=maths.id, name="Maths Final", total_questions=10)

        db.add(bio_exam)
        db.add(phys_exam)
        db.add(chem_exam)
        db.add(eng_exam)
        db.add(maths_exam)
        db.commit()

        # Create questions
        questions = [
            Question(exam_id=bio_exam.id, text="What is the basic unit of life?", option_a="Atom", option_b="Cell", option_c="Molecule", option_d="Tissue", correct_option="B"),
            Question(exam_id=phys_exam.id, text="What is the SI unit of force?", option_a="Newton", option_b="Joule", option_c="Watt", option_d="Pascal", correct_option="A"),
            Question(exam_id=hist_exam.id, text="When did World War II end?", option_a="1944", option_b="1945", option_c="1946", option_d="1947", correct_option="B"),
        ]

        for q in questions:
            db.add(q)

        db.commit()
        print("✅ Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()