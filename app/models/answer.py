from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)  # For exam answers
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option = Column(String)
    is_correct = Column(Boolean)
    timestamp = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    exam = relationship("Exam", back_populates="answers")