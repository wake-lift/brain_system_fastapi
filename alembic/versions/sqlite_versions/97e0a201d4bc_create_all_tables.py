"""Create all tables

Revision ID: 97e0a201d4bc
Revises: 
Create Date: 2024-07-09 11:43:57.798212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97e0a201d4bc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feedback',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=True),
    sa.Column('feedback_text', sa.Text(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('unit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('boughtinproduct',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('unit_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.SmallInteger(), nullable=True),
    sa.Column('product_type', sa.String(length=128), nullable=True),
    sa.Column('comment', sa.String(length=512), nullable=True),
    sa.ForeignKeyConstraint(['unit_id'], ['unit.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('question',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('package', sa.String(length=256), nullable=True),
    sa.Column('tour', sa.String(length=256), nullable=True),
    sa.Column('number', sa.SmallInteger(), nullable=True),
    sa.Column('question_type', sa.Enum('Б', 'БД', 'ДБ', 'И', 'Л', 'Ч', 'ЧБ', 'ЧД', 'Э', 'Я', name='questiontype'), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.Column('pass_criteria', sa.Text(), nullable=True),
    sa.Column('authors', sa.Text(), nullable=True),
    sa.Column('sources', sa.Text(), nullable=True),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('is_condemned', sa.Boolean(), nullable=False),
    sa.Column('is_published', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_question'), 'question', ['question'], unique=False)
    op.create_table('productlink',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bought_in_product_id', sa.Integer(), nullable=True),
    sa.Column('link', sa.String(length=300), nullable=True),
    sa.Column('link_short_name', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['bought_in_product_id'], ['boughtinproduct.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('productlink')
    op.drop_index(op.f('ix_question_question'), table_name='question')
    op.drop_table('question')
    op.drop_table('boughtinproduct')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('unit')
    op.drop_table('feedback')
    # ### end Alembic commands ###
