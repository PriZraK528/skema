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
        sa.Column("full_name", sa.String(length=200), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
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
        "doctor_schedule_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("slot_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("doctor_id", "weekday", name="uq_doctor_weekday"),
    )

    op.create_table(
        "schedule_exceptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exception_date", sa.Date(), nullable=False),
        sa.Column("is_day_off", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("slot_minutes", sa.Integer(), nullable=True),
        sa.Column("reason", sa.String(length=300), nullable=True),
    )
    op.create_index("ix_schedule_exceptions_date", "schedule_exceptions", ["exception_date"])

    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("booked", "cancelled", "completed", name="appointment_status"),
            nullable=False,
            server_default="booked",
        ),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("rescheduled_from_id", sa.Integer(), sa.ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("doctor_id", "starts_at", name="uq_appointment_doctor_starts_at"),
    )
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"])
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index("ix_appointments_starts_at", "appointments", ["starts_at"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "appointment_booked",
                "appointment_reminder",
                "appointment_cancelled",
                "appointment_rescheduled",
                "schedule_changed",
                name="notification_type",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("appointment_id", sa.Integer(), sa.ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("appointments")
    op.drop_table("schedule_exceptions")
    op.drop_table("doctor_schedule_rules")
    op.drop_table("doctors")
    op.drop_table("patients")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS notification_type")
    op.execute("DROP TYPE IF EXISTS appointment_status")
    op.execute("DROP TYPE IF EXISTS user_role")
