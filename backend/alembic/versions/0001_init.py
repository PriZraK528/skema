"""init

Revision ID: 0001_init
Revises: 
Create Date: 2026-05-06

"""

from alembic import op
import sqlalchemy as sa


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "doctor", "patient", "registrar", name="user_role"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
    )
    op.create_index("ix_patients_user_id", "patients", ["user_id"], unique=True)

    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("specialization", sa.String(length=200), nullable=False),
    )
    op.create_index("ix_doctors_user_id", "doctors", ["user_id"], unique=True)

    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("booked", "cancelled", "completed", name="appointment_status"),
            nullable=False,
            server_default="booked",
        ),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("doctor_id", "starts_at", name="uq_appointment_doctor_starts_at"),
    )
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"], unique=False)
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"], unique=False)
    op.create_index("ix_appointments_starts_at", "appointments", ["starts_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_appointments_starts_at", table_name="appointments")
    op.drop_index("ix_appointments_doctor_id", table_name="appointments")
    op.drop_index("ix_appointments_patient_id", table_name="appointments")
    op.drop_table("appointments")

    op.drop_index("ix_doctors_user_id", table_name="doctors")
    op.drop_table("doctors")

    op.drop_index("ix_patients_user_id", table_name="patients")
    op.drop_table("patients")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS appointment_status")
    op.execute("DROP TYPE IF EXISTS user_role")

