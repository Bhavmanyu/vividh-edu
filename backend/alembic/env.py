"""Alembic environment configuration for IndiaLens migrations.

Works with:
  - Local Postgres: postgresql://indialens:pass@localhost/indialens
  - Supabase pooler: postgresql://postgres.REF:PASS@pooler.supabase.com:6543/postgres
  - Railway:        postgresql://user:pass@host/db
  - DATABASE_URL from env (auto-converted to psycopg2 sync format)
"""
import re
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _to_sync_url(url: str) -> str:
    """
    Convert any DATABASE_URL variant to a psycopg2-compatible sync URL.
    - Strips +asyncpg driver suffix
    - Converts postgres:// → postgresql://
    - Adds sslmode=require for Supabase connections
    """
    # postgres:// → postgresql://
    url = re.sub(r'^postgres://', 'postgresql://', url)
    # strip asyncpg or other async driver specifiers
    url = re.sub(r'\+asyncpg', '', url)
    url = re.sub(r'\+aiopg', '', url)
    # Add SSL for Supabase
    if 'supabase.co' in url or 'pooler.supabase' in url:
        if '?' not in url:
            url += '?sslmode=require'
        elif 'sslmode' not in url:
            url += '&sslmode=require'
    return url


# Prefer DATABASE_URL_SYNC, fall back to converting DATABASE_URL
raw_url = os.environ.get(
    "DATABASE_URL_SYNC",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://indialens:indialens_dev@localhost:5432/indialens",
    ),
)
sync_url = _to_sync_url(raw_url)
config.set_main_option("sqlalchemy.url", sync_url)

target_metadata = None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
