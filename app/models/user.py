from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    username = Column(String)
    join_time = Column(DateTime, default=func.now())

    level = Column(String, nullable=True)
    stream = Column(String, nullable=True)

    payment_status = Column(String, default="NOT_PAID")
    access = Column(String, default="LOCKED")

    # Referral system fields
    referral_code = Column(String, unique=True, nullable=True)  # Unique referral code
    referred_by_id = Column(Integer, nullable=True)  # Who referred this user
    total_referrals = Column(Integer, default=0)  # Total successful referrals
    total_commission = Column(Integer, default=0)  # Total ETB earned from referrals
    is_referral_active = Column(Boolean, default=True)  # Whether user can earn more referrals

    # Relationships
    payments = relationship("Payment", back_populates="user")
    answers = relationship("Answer", back_populates="user")
    results = relationship("Result", back_populates="user")
