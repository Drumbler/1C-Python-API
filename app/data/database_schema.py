from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKeyConstraint,
    Integer,
    MetaData,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)


metadata = MetaData()


product_categories = Table(
    "product_categories",
    metadata,
    Column("id", BigInteger, nullable=False, autoincrement=False),
    Column("name", String(255), nullable=False),
    PrimaryKeyConstraint("id", name="product_types_pkey"),
)


product_mapping = Table(
    "product_mapping",
    metadata,
    Column("id", Integer, nullable=False, autoincrement=True),
    Column("file_name", String(50)),
    PrimaryKeyConstraint("id", name="product_mapping_pkey"),
)


products = Table(
    "products",
    metadata,
    Column("id", Integer, nullable=False, autoincrement=True),
    Column("series", Text, nullable=False),
    Column("product_type", Text, nullable=False),
    Column("product_name", Text, nullable=False),
    Column("file_loc", Integer),
    Column("category_id", BigInteger),
    PrimaryKeyConstraint("id", name="products_pkey"),
    UniqueConstraint("series", name="products_series_key"),
    ForeignKeyConstraint(
        ["file_loc"],
        ["product_mapping.id"],
        name="products_file_loc_fkey",
    ),
    ForeignKeyConstraint(
        ["category_id"],
        ["product_categories.id"],
        name="fk_orders_category",
    ),
)


materials = Table(
    "materials",
    metadata,
    Column("id", Integer, nullable=False, autoincrement=True),
    Column("name", Text, nullable=False),
    Column("abbreviation", Text),
    Column("units", Text, nullable=False),
    Column("price", Numeric(9, 2), nullable=False),
    Column("type", Text, nullable=False),
    Column("to_weight_koef", Numeric(9, 2), nullable=False),
    PrimaryKeyConstraint("id", name="materials_pkey"),
    UniqueConstraint("name", name="materials_name_key"),
    CheckConstraint(
        "type = ANY (ARRAY['material'::text, 'semis'::text, 'work'::text, 'option'::text])",
        name="materials_type_check",
    ),
    CheckConstraint(
        "units = ANY (ARRAY['м2'::text, 'м'::text, 'шт'::text, 'коэф'::text])",
        name="materials_units_check",
    ),
)


materials_for_products = Table(
    "materials_for_products",
    metadata,
    Column("product_id", Integer, nullable=False),
    Column("material_id", Integer, nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("misc", Boolean, server_default=text("false")),
    Column("alternative_abbreviations", Text),
    PrimaryKeyConstraint(
        "product_id",
        "material_id",
        name="materials_for_products_pkey",
    ),
    ForeignKeyConstraint(
        ["product_id"],
        ["products.id"],
        name="materials_for_products_product_id_fkey",
    ),
    ForeignKeyConstraint(
        ["material_id"],
        ["materials.id"],
        name="materials_for_products_material_id_fkey",
    ),
)


history_products = Table(
    "history_products",
    metadata,
    Column("id", Integer, nullable=False),
    Column("date", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("new_series", Text),
    Column("new_product_type", Text),
    Column("new_product_name", Text),
    Column("status", Text, nullable=False),
    CheckConstraint(
        "status = ANY (ARRAY['added'::text, 'updated'::text, 'deleted'::text])",
        name="history_products_status_check",
    ),
)


history_materials = Table(
    "history_materials",
    metadata,
    Column("id", Integer, nullable=False),
    Column("date", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("new_name", Text),
    Column("new_abbreviation", Text),
    Column("new_units", Text),
    Column("new_price", Numeric(9, 2)),
    Column("new_type", Text),
    Column("new_to_weight_koef", Numeric(9, 2)),
    Column("status", Text, nullable=False),
    CheckConstraint(
        "new_type = ANY (ARRAY['material'::text, 'semis'::text, 'work'::text, 'option'::text])",
        name="history_materials_new_type_check",
    ),
    CheckConstraint(
        "new_units = ANY (ARRAY['м2'::text, 'м'::text, 'шт'::text, 'коэф'::text])",
        name="history_materials_new_units_check",
    ),
    CheckConstraint(
        "status = ANY (ARRAY['added'::text, 'updated'::text, 'deleted'::text])",
        name="history_materials_status_check",
    ),
)


history_materials_for_products = Table(
    "history_materials_for_products",
    metadata,
    Column("product_id", Integer, nullable=False),
    Column("material_id", Integer, nullable=False),
    Column("new_quantity", Integer),
    Column(
        "date",
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Column("status", Text, nullable=False),
    PrimaryKeyConstraint(
        "product_id",
        "material_id",
        "date",
        name="history_materials_for_products_pkey",
    ),
    CheckConstraint(
        "status = ANY (ARRAY['added'::text, 'updated'::text, 'deleted'::text])",
        name="history_materials_for_products_status_check",
    ),
)


calculated_products = Table(
    "calculated_products",
    metadata,
    Column("series", Text, nullable=False),
    Column("parameters", Text, nullable=False),
    Column("cost", Float, nullable=False),
    Column("category_id", BigInteger),
    PrimaryKeyConstraint("series", "parameters", name="pk_calculated_products"),
    UniqueConstraint(
        "series",
        "parameters",
        name="calculated_products_series_parameters_key",
    ),
    ForeignKeyConstraint(
        ["category_id"],
        ["product_categories.id"],
        name="fk_orders_category",
    ),
)
