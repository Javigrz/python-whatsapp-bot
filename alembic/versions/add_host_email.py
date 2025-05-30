"""add host email

Revision ID: add_host_email
Revises: 
Create Date: 2024-03-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_host_email'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Añadir columna host_email
    op.add_column('clients', sa.Column('host_email', sa.String(), nullable=True))
    
    # Hacer la columna NOT NULL después de añadirla
    op.alter_column('clients', 'host_email',
               existing_type=sa.String(),
               nullable=False)


def downgrade() -> None:
    # Eliminar columna host_email
    op.drop_column('clients', 'host_email') 