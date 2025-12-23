from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.base import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)

    # Relationships
    exams = relationship("Exam", back_populates="course")