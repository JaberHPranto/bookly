"""add user id foreign key is book model

Revision ID: 79f305215946
Revises: 413ea2636c56
Create Date: 2025-12-15 19:05:40.407861

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "79f305215946"
down_revision: Union[str, Sequence[str], None] = "413ea2636c56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # No-op: user_id column and foreign key already created in init migration
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # No-op: user_id column and foreign key handled by init migration
    pass
