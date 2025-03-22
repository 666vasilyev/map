"""empty message

Revision ID: 19200e4dbaae
Revises: b51f7542f175, bfcbec443e39
Create Date: 2025-03-22 15:28:24.131908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19200e4dbaae'
down_revision: Union[str, None] = ('b51f7542f175', 'bfcbec443e39')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
