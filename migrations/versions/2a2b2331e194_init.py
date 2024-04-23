"""init

Revision ID: 2a2b2331e194
Revises: 
Create Date: 2024-04-23 12:44:12.262911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a2b2331e194'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('password', sa.String(length=1024), nullable=False),
    sa.Column('avatar', sa.String(length=255), nullable=True),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.Column('registered_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('confirmed', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('image_path', sa.String(), nullable=False),
    sa.Column('mime_type', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('count_tags', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_images_id'), 'images', ['id'], unique=False)
    op.create_index(op.f('ix_images_image_path'), 'images', ['image_path'], unique=False)
    op.create_index(op.f('ix_images_mime_type'), 'images', ['mime_type'], unique=False)
    op.create_index(op.f('ix_images_name'), 'images', ['name'], unique=False)
    op.create_index(op.f('ix_images_size'), 'images', ['size'], unique=False)
    op.create_index(op.f('ix_images_title'), 'images', ['title'], unique=False)
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('image_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['image_id'], ['images.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_id'), 'comments', ['id'], unique=False)
    op.create_index(op.f('ix_comments_text'), 'comments', ['text'], unique=False)
    op.create_table('image_tag_association',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('image_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['image_id'], ['images.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tag_id', 'image_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('image_tag_association')
    op.drop_index(op.f('ix_comments_text'), table_name='comments')
    op.drop_index(op.f('ix_comments_id'), table_name='comments')
    op.drop_table('comments')
    op.drop_index(op.f('ix_images_title'), table_name='images')
    op.drop_index(op.f('ix_images_size'), table_name='images')
    op.drop_index(op.f('ix_images_name'), table_name='images')
    op.drop_index(op.f('ix_images_mime_type'), table_name='images')
    op.drop_index(op.f('ix_images_image_path'), table_name='images')
    op.drop_index(op.f('ix_images_id'), table_name='images')
    op.drop_table('images')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')
    # ### end Alembic commands ###