import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.base import Base
from app.database.session import engine

# import all models
from app.models.user import User
from app.models.payment import Payment
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.exam import Exam
from app.models.question import Question
from app.models.answer import Answer
from app.models.result import Result

def create_database():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database and tables created successfully!")

def reset_database():
    """Drop all tables and recreate them"""
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database reset and tables created successfully!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_database()
    else:
        create_database()
