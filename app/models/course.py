from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exams = relationship("Exam", back_populates="course")
    chapters = relationship("Chapter", back_populates="course", cascade="all, delete-orphan")
