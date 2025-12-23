from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String, nullable=False)
    total_questions = Column(Integer)
    time_limit = Column(Integer, nullable=True)  # Time limit in minutes
    total_marks = Column(Integer, nullable=True)  # Total possible marks
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="exams")
    questions = relationship("Question", back_populates="exam")
    results = relationship("Result", back_populates="exam")
    answers = relationship("Answer", back_populates="exam")
