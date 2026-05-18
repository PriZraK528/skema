"""availability slots

Revision ID: 0002_availability_slots
Revises: 0001_init
Create Date: 2026-05-18

"""

from alembic import op
import sqlalchemy as sa


revision = "0002_availability_slots"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "doctor_availability_slots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("doctor_id", "starts_at", name="uq_doctor_availability_starts_at"),
    )
    op.create_index("ix_doctor_availability_slots_doctor_id", "doctor_availability_slots", ["doctor_id"])
    op.create_index("ix_doctor_availability_slots_starts_at", "doctor_availability_slots", ["starts_at"])


def downgrade() -> None:
    op.drop_table("doctor_availability_slots")
