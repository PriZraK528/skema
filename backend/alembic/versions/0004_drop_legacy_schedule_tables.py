"""drop legacy schedule tables

Revision ID: 0004_drop_legacy_schedule_tables
Revises: 0003_remove_registrar_fix_booking
Create Date: 2026-06-02

"""

from alembic import op


revision = "0004_drop_legacy_schedule_tables"
down_revision = "0003_remove_registrar_fix_booking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("schedule_exceptions")
    op.drop_table("doctor_schedule_rules")


def downgrade() -> None:
    import sqlalchemy as sa

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
