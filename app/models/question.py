from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    text = Column(Text, nullable=False)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String, nullable=False)  # Fixed: matches admin handler
    course = Column(String)  # Added: matches admin handler
    difficulty = Column(String)  # Added: matches admin handler

    # Relationships
    exam = relationship("Exam", back_populates="questions")
    answers = relationship("Answer", back_populates="question")
