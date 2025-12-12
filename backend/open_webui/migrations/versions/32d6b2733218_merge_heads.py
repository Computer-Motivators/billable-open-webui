"""merge heads: knowledge_file and token_usage

Revision ID: 32d6b2733218
Revises: 3e0e00844bb0, e1f2a3b4c5d6
Create Date: 2025-01-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db

# revision identifiers, used by Alembic.
revision: str = "32d6b2733218"
down_revision: Union[str, tuple] = ("3e0e00844bb0", "e1f2a3b4c5d6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

