from sqlalchemy import select

from app.models import Doctor, Patient, User, UserRole
from app.security import hash_password

SEED_PASSWORD = "Password123!"


def run_seed() -> None:
    from app.db import SessionLocal

    db = SessionLocal()
    try:
        if db.scalar(select(User).limit(1)):
            return

        admin = User(
            email="admin@clinic.example",
            password_hash=hash_password(SEED_PASSWORD),
            role=UserRole.admin,
            full_name="Администратор",
            phone="+70000000001",
        )
        db.add(admin)

        doc_user = User(
            email="doctor@clinic.example",
            password_hash=hash_password(SEED_PASSWORD),
            role=UserRole.doctor,
            full_name="Иванов Иван",
            phone="+70000000002",
        )
        db.add(doc_user)
        db.flush()
        doctor = Doctor(
            user_id=doc_user.id,
            full_name="Иванов Иван",
            specialization="Терапевт",
        )
        db.add(doctor)
        db.flush()

        pat_user = User(
            email="patient@clinic.example",
            password_hash=hash_password(SEED_PASSWORD),
            role=UserRole.patient,
            full_name="Петров Пётр",
            phone="+70000000004",
        )
        db.add(pat_user)
        db.flush()
        db.add(
            Patient(
                user_id=pat_user.id,
                full_name="Петров Пётр",
                phone="+70000000004",
            )
        )

        db.commit()
    finally:
        db.close()
