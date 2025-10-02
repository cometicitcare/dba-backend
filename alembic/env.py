from __future__ import annotations
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from dotenv import load_dotenv
from pathlib import Path

import os, sys
from pathlib import Path
# Ensure project root (the folder with app/ and alembic/) is importable
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Force-load .env from project root
load_dotenv(BASE_DIR / ".env")

from app.core.config import settings

# (optional) quick sanity prints during setup; remove after it works

print("POSTGRES_HOST:", os.getenv("POSTGRES_HOST"), file=sys.stderr)

# this is the Alembic Config object, which provides access to the values
config = context.config
# Escape % for ConfigParser interpolation syntax
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))


# set DB URL from env at runtime if provided
import os
if os.getenv("DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL").replace("%", "%%"))


# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Import metadata
from app.db.base import Base # noqa: E402


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()




def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
    )


    with context.begin_transaction():
        context.run_migrations()




async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )


    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


    await connectable.dispose()




if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())