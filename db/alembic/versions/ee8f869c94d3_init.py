"""Init

Revision ID: ee8f869c94d3
Revises: 
Create Date: 2020-04-09 14:19:07.532524

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ee8f869c94d3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "resources",
        sa.Column("resource_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("resource_id"),
    )
    op.create_table(
        "zoon_places",
        sa.Column("zoon_place_id", sa.Integer(), nullable=False),
        sa.Column("zoon_place_name", sa.String(), nullable=True),
        sa.Column("zoon_place_url", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("zoon_place_id"),
    )
    op.create_table(
        "crawling_info",
        sa.Column("crawling_info_id", sa.Integer(), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("crawl_start_time", sa.DateTime(), nullable=True),
        sa.Column("crawl_end_time", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["resource_id"], ["resources.resource_id"],),
        sa.PrimaryKeyConstraint("crawling_info_id"),
    )
    op.create_table(
        "zoon_dishes",
        sa.Column("zoon_dish_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("category_url", sa.String(), nullable=True),
        sa.Column("price", sa.String(), nullable=True),
        sa.Column("zoon_place_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["zoon_place_id"], ["zoon_places.zoon_place_id"],),
        sa.PrimaryKeyConstraint("zoon_dish_id"),
    )
    op.create_table(
        "zoon_places_info",
        sa.Column("zoon_places_info_id", sa.Integer(), nullable=False),
        sa.Column("zoon_place_id", sa.Integer(), nullable=True),
        sa.Column("phone_number", sa.String(), nullable=True),
        sa.Column("adress", sa.String(), nullable=True),
        sa.Column("price_range", sa.String(), nullable=True),
        sa.Column("schedule", sa.String(), nullable=True),
        sa.Column("original_link", sa.String(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["zoon_place_id"], ["zoon_places.zoon_place_id"],),
        sa.PrimaryKeyConstraint("zoon_places_info_id"),
    )
    op.create_table(
        "responses",
        sa.Column("response_id", sa.Integer(), nullable=False),
        sa.Column("response_time", sa.DateTime(), nullable=True),
        sa.Column("query_location", sa.String(), nullable=True),
        sa.Column("query_dish", sa.String(), nullable=True),
        sa.Column("zoon_place_id", sa.Integer(), nullable=True),
        sa.Column("zoon_dish_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["zoon_dish_id"], ["zoon_dishes.zoon_dish_id"],),
        sa.ForeignKeyConstraint(["zoon_place_id"], ["zoon_places.zoon_place_id"],),
        sa.PrimaryKeyConstraint("response_id"),
    )


def downgrade():
    op.drop_table("responses")
    op.drop_table("zoon_places_info")
    op.drop_table("zoon_dishes")
    op.drop_table("crawling_info")
    op.drop_table("zoon_places")
    op.drop_table("resources")
