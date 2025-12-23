from sqlalchemy import Column, Integer, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    score = Column(Integer)
    percentage = Column(Float)
    completed_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="results")
    exam = relationship("Exam", back_populates="results")