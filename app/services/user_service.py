from app.database.session import SessionLocal
from app.models.user import User

def get_or_create_user(tg_user):
    db = SessionLocal()

    user = db.query(User).filter_by(telegram_id=tg_user.id).first()

    if not user:
        user = User(
            telegram_id=tg_user.id,
            full_name=tg_user.full_name,
            username=tg_user.username
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    db.close()
    return user