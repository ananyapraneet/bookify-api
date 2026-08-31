"""add user roles

Revision ID: c2bcb9ccc137
Revises: e12b4e2cd487
Create Date: 2026-08-29 19:16:58.102792

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.

revision: str = "c2bcb9ccc137"
down_revision: str | Sequence[str] | None = "e12b4e2cd487"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    user_role = sa.Enum(
        "customer",
        "provider",
        "admin",
        name="userrole",
    )

    user_role.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(length=50),
        type_=user_role,
        existing_nullable=False,
        postgresql_using="role::text::userrole",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "users",
        "role",
        existing_type=sa.Enum(
            "customer",
            "provider",
            "admin",
            name="userrole",
        ),
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
    )

    user_role = sa.Enum(
        "customer",
        "provider",
        "admin",
        name="userrole",
    )

    user_role.drop(op.get_bind(), checkfirst=True)
