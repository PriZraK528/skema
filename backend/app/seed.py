from datetime import time

from sqlalchemy import select

from app.models import Doctor, DoctorScheduleRule, Patient, User, UserRole
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

        for weekday in range(0, 5):
            db.add(
                DoctorScheduleRule(
                    doctor_id=doctor.id,
                    weekday=weekday,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    slot_minutes=30,
                )
            )

        reg = User(
            email="registrar@clinic.example",
            password_hash=hash_password(SEED_PASSWORD),
            role=UserRole.registrar,
            full_name="Регистратор",
            phone="+70000000003",
        )
        db.add(reg)

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
