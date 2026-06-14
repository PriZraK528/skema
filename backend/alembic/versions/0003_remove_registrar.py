"""remove registrar role and fix rebooking after cancel

Revision ID: 0003_remove_registrar
Revises: 0002_availability_slots
Create Date: 2026-06-02

"""

from alembic import op


revision = "0003_remove_registrar"
down_revision = "0002_availability_slots"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM users WHERE email = 'registrar@clinic.example'")
    op.execute("UPDATE users SET role = 'admin' WHERE role = 'registrar'")
    op.execute(
        "ALTER TABLE appointments DROP CONSTRAINT IF EXISTS uq_appointment_doctor_starts_at"
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_appointment_doctor_starts_at_booked
        ON appointments (doctor_id, starts_at)
        WHERE status = 'booked'
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role_old') THEN
                NULL;
            ELSIF EXISTS (
                SELECT 1
                FROM pg_enum e
                JOIN pg_type t ON e.enumtypid = t.oid
                WHERE t.typname = 'user_role' AND e.enumlabel = 'registrar'
            ) THEN
                ALTER TYPE user_role RENAME TO user_role_old;
                CREATE TYPE user_role AS ENUM ('admin', 'doctor', 'patient');
                ALTER TABLE users
                    ALTER COLUMN role TYPE user_role
                    USING role::text::user_role;
                DROP TYPE user_role_old;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TYPE user_role RENAME TO user_role_old")
    op.execute(
        "CREATE TYPE user_role AS ENUM ('admin', 'doctor', 'patient', 'registrar')"
    )
    op.execute(
        "ALTER TABLE users ALTER COLUMN role TYPE user_role "
        "USING role::text::user_role"
    )
    op.execute("DROP TYPE user_role_old")
    op.execute("DROP INDEX IF EXISTS uq_appointment_doctor_starts_at_booked")
    op.create_unique_constraint(
        "uq_appointment_doctor_starts_at",
        "appointments",
        ["doctor_id", "starts_at"],
    )
