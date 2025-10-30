"""Initial migration with pgvector extension

Revision ID: 3b2478be7244
Revises: 
Create Date: 2025-10-04 19:39:27.027835

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '3b2478be7244'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('picture_url', sa.String(length=500), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    
    # Create collections table
    op.create_table('collections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_collections_user_id'), 'collections', ['user_id'], unique=False)
    
    # Create authors table
    op.create_table('authors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('affiliation', sa.String(length=500), nullable=True),
        sa.Column('orcid', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create papers table
    op.create_table('papers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('collection_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('doi', sa.String(length=255), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('venue', sa.String(length=255), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('pdf_url', sa.String(length=500), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('added_via', sa.String(length=50), nullable=False),
        sa.Column('raw_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_papers_collection_id'), 'papers', ['collection_id'], unique=False)
    op.create_index(op.f('ix_papers_doi'), 'papers', ['doi'], unique=False)
    
    # Create paper_authors table
    op.create_table('paper_authors',
        sa.Column('paper_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('paper_id', 'author_id')
    )
    
    # Create citations table
    op.create_table('citations',
        sa.Column('src_paper_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dst_doi', sa.String(length=255), nullable=True),
        sa.Column('resolved_paper_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('dst_title', sa.Text(), nullable=True),
        sa.Column('dst_year', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['resolved_paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['src_paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('src_paper_id', 'dst_doi'),
        sa.UniqueConstraint('src_paper_id', 'dst_doi', name='uq_citations_src_dst')
    )
    op.create_index(op.f('ix_citations_resolved_paper_id'), 'citations', ['resolved_paper_id'], unique=False)
    op.create_index(op.f('ix_citations_src_paper_id'), 'citations', ['src_paper_id'], unique=False)
    
    # Create chunks table
    op.create_table('chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paper_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section', sa.String(length=100), nullable=False),
        sa.Column('ord', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chunks_paper_id_ord'), 'chunks', ['paper_id', 'ord'], unique=False)
    
    # Create chunk_embeddings table
    op.create_table('chunk_embeddings',
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.ForeignKeyConstraint(['chunk_id'], ['chunks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('chunk_id')
    )
    
    # Create paper_summaries table
    op.create_table('paper_summaries',
        sa.Column('paper_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('abstract_summary', sa.Text(), nullable=True),
        sa.Column('intro_summary', sa.Text(), nullable=True),
        sa.Column('conclusion_summary', sa.Text(), nullable=True),
        sa.Column('tldr', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('paper_id')
    )
    
    # Create gap_insights table
    op.create_table('gap_insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('collection_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('insight', sa.Text(), nullable=False),
        sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('score', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('gap_insights')
    op.drop_table('paper_summaries')
    op.drop_table('chunk_embeddings')
    op.drop_table('chunks')
    op.drop_table('citations')
    op.drop_table('paper_authors')
    op.drop_table('papers')
    op.drop_table('authors')
    op.drop_table('collections')
    op.drop_table('users')
    
    # Drop pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector')
