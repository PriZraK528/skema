from alembic import op

revision = "0006_remove_registrar_user"
down_revision = "0005_drop_reschedule"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM users WHERE email = 'registrar@clinic.example'")


def downgrade() -> None:
    pass
