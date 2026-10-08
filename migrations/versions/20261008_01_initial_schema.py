"""Baseline of the restored calculation database schema.

Revision ID: 20261008_01
Revises:
Create Date: 2026-10-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261008_01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_categories",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name="product_types_pkey"),
    )
    op.create_table(
        "product_mapping",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("file_name", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id", name="product_mapping_pkey"),
    )
    op.create_table(
        "materials",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("abbreviation", sa.Text(), nullable=True),
        sa.Column("units", sa.Text(), nullable=False),
        sa.Column("price", sa.Numeric(precision=9, scale=2), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("to_weight_koef", sa.Numeric(precision=9, scale=2), nullable=False),
        sa.CheckConstraint(
            "type = ANY (ARRAY['material'::text, 'semis'::text, 'work'::text, 'option'::text])",
            name="materials_type_check",
        ),
        sa.CheckConstraint(
            "units = ANY (ARRAY['м2'::text, 'м'::text, 'шт'::text, 'коэф'::text])",
            name="materials_units_check",
        ),
        sa.PrimaryKeyConstraint("id", name="materials_pkey"),
        sa.UniqueConstraint("name", name="materials_name_key"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("series", sa.Text(), nullable=False),
        sa.Column("product_type", sa.Text(), nullable=False),
        sa.Column("product_name", sa.Text(), nullable=False),
        sa.Column("file_loc", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["product_categories.id"],
            name="fk_orders_category",
        ),
        sa.ForeignKeyConstraint(
            ["file_loc"],
            ["product_mapping.id"],
            name="products_file_loc_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="products_pkey"),
        sa.UniqueConstraint("series", name="products_series_key"),
    )
    op.create_table(
        "materials_for_products",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("misc", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("alternative_abbreviations", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["materials.id"],
            name="materials_for_products_material_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="materials_for_products_product_id_fkey",
        ),
        sa.PrimaryKeyConstraint(
            "product_id",
            "material_id",
            name="materials_for_products_pkey",
        ),
    )
    op.create_table(
        "history_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("new_series", sa.Text(), nullable=True),
        sa.Column("new_product_type", sa.Text(), nullable=True),
        sa.Column("new_product_name", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "status = ANY (ARRAY['added'::text, 'updated'::text, 'deleted'::text])",
            name="history_products_status_check",
        ),
    )
    op.create_table(
        "history_materials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("new_name", sa.Text(), nullable=True),
        sa.Column("new_abbreviation", sa.Text(), nullable=True),
        sa.Column("new_units", sa.Text(), nullable=True),
        sa.Column("new_price", sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column("new_type", sa.Text(), nullable=True),
        sa.Column("new_to_weight_koef", sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "new_type = ANY (ARRAY['material'::text, 'semis'::text, 'work'::text, 'option'::text])",
            name="history_materials_new_type_check",
        ),
        sa.CheckConstraint(
            "new_units = ANY (ARRAY['м2'::text, 'м'::text, 'шт'::text, 'коэф'::text])",
            name="history_materials_new_units_check",
        ),
        sa.CheckConstraint(
            "status = ANY (ARRAY['added'::text, 'updated'::text, 'deleted'::text])",
            name="history_materials_status_check",
        ),
    )
    op.create_table(
        "history_materials_for_products",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("new_quantity", sa.Integer(), nullable=True),
        sa.Column(
            "date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("status", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "status = ANY (ARRAY['added'::text, 'updated'::text, 'deleted'::text])",
            name="history_materials_for_products_status_check",
        ),
        sa.PrimaryKeyConstraint(
            "product_id",
            "material_id",
            "date",
            name="history_materials_for_products_pkey",
        ),
    )
    op.create_table(
        "calculated_products",
        sa.Column("series", sa.Text(), nullable=False),
        sa.Column("parameters", sa.Text(), nullable=False),
        sa.Column("cost", sa.Float(), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["product_categories.id"],
            name="fk_orders_category",
        ),
        sa.PrimaryKeyConstraint(
            "series",
            "parameters",
            name="pk_calculated_products",
        ),
    )
    op.create_unique_constraint(
        "calculated_products_series_parameters_key",
        "calculated_products",
        ["series", "parameters"],
    )

    _create_audit_functions()
    _create_audit_triggers()


def downgrade() -> None:
    op.drop_table("calculated_products")
    op.drop_table("history_materials_for_products")
    op.drop_table("history_materials")
    op.drop_table("history_products")
    op.drop_table("materials_for_products")
    op.drop_table("products")
    op.drop_table("materials")
    op.drop_table("product_mapping")
    op.drop_table("product_categories")

    for function_name in (
        "trg_materials_delete_func",
        "trg_materials_for_products_delete_func",
        "trg_materials_for_products_insert_func",
        "trg_materials_for_products_update_func",
        "trg_materials_insert_func",
        "trg_materials_update_func",
        "trg_products_delete_func",
        "trg_products_insert_func",
        "trg_products_update_func",
    ):
        op.execute(f"DROP FUNCTION public.{function_name}()")


def _create_audit_functions() -> None:
    statements = (
        """
        CREATE FUNCTION public.trg_materials_delete_func() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO history_materials (id, status)
            VALUES (OLD.id, 'deleted');
            RETURN OLD;
        END;
        $$
        """,
        """
        CREATE FUNCTION public.trg_materials_for_products_delete_func() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO history_materials_for_products (product_id, material_id, status)
            VALUES (OLD.product_id, OLD.material_id, 'deleted');
            RETURN OLD;
        END;
        $$
        """,
        """
        CREATE FUNCTION public.trg_materials_for_products_insert_func() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO history_materials_for_products
                (product_id, material_id, new_quantity, status)
            VALUES (NEW.product_id, NEW.material_id, NEW.quantity, 'added');
            RETURN NEW;
        END;
        $$
        """,
        """
        CREATE FUNCTION public.trg_materials_for_products_update_func() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO history_materials_for_products
                (product_id, material_id, new_quantity, status)
            VALUES (
                OLD.product_id,
                OLD.material_id,
                CASE WHEN NEW.quantity != OLD.quantity THEN NEW.quantity ELSE NULL END,
                'updated'
            );
            RETURN NEW;
        END;
        $$
        """,
        """
        CREATE FUNCTION public.trg_materials_insert_func() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO history_materials
                (id, new_name, new_abbreviation, new_units, new_price, new_type,
                 new_to_weight_koef, status)
            VALUES (
                NEW.id, NEW.name, NEW.abbreviation, NEW.units, NEW.price, NEW.type,
                NEW.to_weight_koef, 'added'
            );
            RETURN NEW;
        END;
        $$
        """,
        """
        CREATE FUNCTION public.trg_materials_update_func() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO history_materials
                (id, new_name, new_abbreviation, new_units, new_price, new_type,
                 new_to_weight_koef, status)
            VALUES (
                OLD.id,
                CASE WHEN NEW.name != OLD.name THEN NEW.name ELSE NULL END,
                CASE WHEN NEW.abbreviation != OLD.abbreviation THEN NEW.abbreviation ELSE NULL END,
                CASE WHEN NEW.units != OLD.units THEN NEW.units ELSE NULL END,
                CASE WHEN NEW.price != OLD.price THEN NEW.price ELSE NULL END,
                CASE WHEN NEW.type != OLD.type THEN NEW.type ELSE NULL END,
                CASE WHEN NEW.to_weight_koef != OLD.to_weight_koef THEN NEW.to_weight_koef ELSE NULL END,
                'updated'
            );
            RETURN NEW;
        END;
        $$
        """,
        """
        CREATE FUNCTION public.trg_products_delete_func() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO history_products (id, status)
            VALUES (OLD.id, 'deleted');
            RETURN OLD;
        END;
        $$
        """,
        """
        CREATE FUNCTION public.trg_products_insert_func() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO history_products
                (id, new_series, new_product_type, new_product_name, status)
            VALUES (
                NEW.id, NEW.series, NEW.product_type, NEW.product_name, 'added'
            );
            RETURN NEW;
        END;
        $$
        """,
        """
        CREATE FUNCTION public.trg_products_update_func() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO history_products
                (id, new_series, new_product_type, new_product_name, status)
            VALUES (
                OLD.id,
                CASE WHEN NEW.series != OLD.series THEN NEW.series ELSE NULL END,
                CASE WHEN NEW.product_type != OLD.product_type THEN NEW.product_type ELSE NULL END,
                CASE WHEN NEW.product_name != OLD.product_name THEN NEW.product_name ELSE NULL END,
                'updated'
            );
            RETURN NEW;
        END;
        $$
        """,
    )
    for statement in statements:
        op.execute(statement)


def _create_audit_triggers() -> None:
    statements = (
        "CREATE TRIGGER trg_materials_delete AFTER DELETE ON public.materials "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_materials_delete_func()",
        "CREATE TRIGGER trg_materials_for_products_delete "
        "AFTER DELETE ON public.materials_for_products FOR EACH ROW "
        "EXECUTE FUNCTION public.trg_materials_for_products_delete_func()",
        "CREATE TRIGGER trg_materials_for_products_insert "
        "AFTER INSERT ON public.materials_for_products FOR EACH ROW "
        "EXECUTE FUNCTION public.trg_materials_for_products_insert_func()",
        "CREATE TRIGGER trg_materials_for_products_update "
        "AFTER UPDATE ON public.materials_for_products FOR EACH ROW "
        "EXECUTE FUNCTION public.trg_materials_for_products_update_func()",
        "CREATE TRIGGER trg_materials_insert AFTER INSERT ON public.materials "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_materials_insert_func()",
        "CREATE TRIGGER trg_materials_update AFTER UPDATE ON public.materials "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_materials_update_func()",
        "CREATE TRIGGER trg_products_delete AFTER DELETE ON public.products "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_products_delete_func()",
        "CREATE TRIGGER trg_products_insert AFTER INSERT ON public.products "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_products_insert_func()",
        "CREATE TRIGGER trg_products_update AFTER UPDATE ON public.products "
        "FOR EACH ROW EXECUTE FUNCTION public.trg_products_update_func()",
    )
    for statement in statements:
        op.execute(statement)
