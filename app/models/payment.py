from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    proof = Column(String)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="payments")