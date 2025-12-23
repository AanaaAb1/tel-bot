from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.admin_panel.auth import verify_admin
from app.admin_panel.deps import get_db
from app.admin_panel.schemas import (
    UserOut,
    PaymentOut,
    ExamResultOut
)

from app.models.user import User
from app.models.payment import Payment
from app.models.exam import Exam
from app.services.payment_service import approve_payment

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(verify_admin)]
)

# ---------------- USERS ----------------

@router.get("/users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# ---------------- PAYMENTS ----------------

@router.get("/payments", response_model=list[PaymentOut])
def get_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()

@router.post("/payments/{payment_id}/approve")
def approve_payment_endpoint(payment_id: int, db: Session = Depends(get_db)):
    approve_payment(payment_id)
    return {"message": "Payment approved"}

# ---------------- EXAMS ----------------

@router.get("/exams", response_model=list[ExamResultOut])
def get_exam_results(db: Session = Depends(get_db)):
    return db.query(Exam).all()