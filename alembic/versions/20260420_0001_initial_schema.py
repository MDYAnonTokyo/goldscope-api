"""Create initial GoldScope schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260420_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "gold_prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("usd_oz", sa.Float(), nullable=False),
        sa.Column("gbp_oz", sa.Float(), nullable=True),
        sa.Column("eur_oz", sa.Float(), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_date", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_gold_prices_price_date", "gold_prices", ["price_date"], unique=True)

    op.create_table(
        "price_alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("condition_type", sa.String(length=20), nullable=False),
        sa.Column("threshold_value", sa.Float(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_price_alerts_user_id", "price_alerts", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_price_alerts_user_id", table_name="price_alerts")
    op.drop_table("price_alerts")
    op.drop_index("ix_gold_prices_price_date", table_name="gold_prices")
    op.drop_table("gold_prices")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
