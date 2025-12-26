from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    order_index = Column(Integer, default=0)  # For ordering chapters within a course
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="chapters")
    questions = relationship("Question", back_populates="chapter")

