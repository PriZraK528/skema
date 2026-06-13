"""drop unused reschedule column

Revision ID: 0005_drop_reschedule
Revises: 0004_drop_legacy_schedule_tables
Create Date: 2026-06-02

"""

from alembic import op


revision = "0005_drop_reschedule"
down_revision = "0004_drop_legacy_schedule_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("appointments", "rescheduled_from_id")


def downgrade() -> None:
    import sqlalchemy as sa

    op.add_column(
        "appointments",
        sa.Column(
            "rescheduled_from_id",
            sa.Integer(),
            sa.ForeignKey("appointments.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
