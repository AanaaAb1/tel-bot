from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)  # New: links to chapter
    text = Column(Text, nullable=False)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String, nullable=False)
    course = Column(String)  # Keep for backward compatibility
    explanation = Column(Text)  # Added explanation field
    difficulty = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exam = relationship("Exam", back_populates="questions")
    chapter = relationship("Chapter", back_populates="questions")
    answers = relationship("Answer", back_populates="question")
