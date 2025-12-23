from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True)
    
    # The user who referred someone
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # The user who was referred
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Referral status
    status = Column(String, default="PENDING")  # PENDING, COMPLETED, REWARDED
    
    # When the referral was made
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # When the referral was completed (invited user paid)
    completed_at = Column(DateTime, nullable=True)
    
    # Commission earned (30 ETB)
    commission_earned = Column(Integer, default=30)
    
    # Whether commission has been paid
    commission_paid = Column(Boolean, default=False)
    
    # Relationships - removed problematic back_populates references

