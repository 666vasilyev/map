"""rename status to object_status

Revision ID: ab5cdd9fbb0c
Revises: b525500d9741
Create Date: 2025-02-24 17:56:39.942209

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab5cdd9fbb0c'
down_revision: Union[str, None] = 'b525500d9741'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Переименовывает колонку `status` в `object_status`, сохраняя данные.
    """

    # ✅ 1. Добавляем новую колонку `object_status`
    op.add_column('objects', sa.Column('object_status', sa.Integer(), nullable=True))  # Временно NULL

    # ✅ 2. Копируем данные из `status` в `object_status`
    op.execute("UPDATE objects SET object_status = status")

    # ✅ 3. Делаем `object_status` NOT NULL
    op.alter_column('objects', 'object_status', nullable=False)

    # ✅ 4. Удаляем старую колонку `status`
    op.drop_column('objects', 'status')


def downgrade() -> None:
    """
    Откатывает изменения, возвращая `status` вместо `object_status`.
    """

    # ✅ 1. Добавляем колонку `status` обратно (временно NULL)
    op.add_column('objects', sa.Column('status', sa.Integer(), nullable=True))

    # ✅ 2. Копируем данные обратно в `status`
    op.execute("UPDATE objects SET status = object_status")

    # ✅ 3. Делаем `status` NOT NULL
    op.alter_column('objects', 'status', nullable=False)

    # ✅ 4. Удаляем колонку `object_status`
    op.drop_column('objects', 'object_status')
