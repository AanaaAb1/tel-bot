from app.database.session import SessionLocal
from app.models.payment import Payment
from app.models.user import User
from app.config.constants import (
    PAYMENT_PENDING,
    PAYMENT_APPROVED,
    PAYMENT_REJECTED,
    ACCESS_UNLOCKED
)

def create_payment(user_id, proof):
    """Create a new payment and return the payment object"""
    db = SessionLocal()

    try:
        payment = Payment(
            user_id=user_id,
            proof=proof,
            status=PAYMENT_PENDING
        )
        db.add(payment)
        db.commit()
        
        # Refresh to get the ID
        db.refresh(payment)
        return payment
        
    except Exception as e:
        print(f"Error creating payment: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def approve_payment(payment_id):
    """Approve payment and return the payment object"""
    db = SessionLocal()

    try:
        payment = db.query(Payment).filter_by(id=payment_id).first()
        user = db.query(User).filter_by(id=payment.user_id).first()

        if payment and user:
            payment.status = PAYMENT_APPROVED
            user.payment_status = PAYMENT_APPROVED
            user.access = ACCESS_UNLOCKED
            db.commit()
            db.refresh(payment)  # Refresh to get updated data
            return payment
        else:
            return None
    except Exception as e:
        print(f"Error approving payment: {e}")
        return None
    finally:
        db.close()

def reject_payment(payment_id):
    """Reject payment and return the payment object"""
    db = SessionLocal()

    try:
        payment = db.query(Payment).filter_by(id=payment_id).first()

        if payment:
            payment.status = PAYMENT_REJECTED
            db.commit()
            db.refresh(payment)  # Refresh to get updated data
            return payment
        else:
            return None
    except Exception as e:
        print(f"Error rejecting payment: {e}")
        return None
    finally:
        db.close()

def process_referral_commission(user_id):
    """Process referral commission when user completes payment"""
    from app.handlers.profile_handler import process_referral_commission_sync
    
    # Call the sync version that doesn't use Telegram API
    return process_referral_commission_sync(user_id)
