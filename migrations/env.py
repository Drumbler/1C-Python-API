from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import URL

from app.data.database_schema import metadata


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

load_dotenv()


def database_url() -> str:
    missing = [
        name
        for name in ("DB_USER", "DB_PASS", "DB_IP", "DB_PORT", "DB_NAME")
        if not os.getenv(name)
    ]
    if missing:
        names = ", ".join(missing)
        raise RuntimeError(f"Missing database environment variables: {names}")

    return URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        host=os.environ["DB_IP"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    ).render_as_string(hide_password=False)


config.set_main_option("sqlalchemy.url", database_url().replace("%", "%%"))
target_metadata = metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
