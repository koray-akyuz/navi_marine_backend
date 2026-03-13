# migrations/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

import sys
from pathlib import Path

# Thêm path để python biết thư mục hiện tại là package root
sys.path.insert(0, str(Path(__file__).parent.parent))

# 1. Kendi modellerimizi ve Base'i import ediyoruz
from database import Base, DATABASE_URL
from models.spatial import SeaArea
from models.reports import FishReport # Birazdan ekleyeceğimiz model

# Alembic Config objesi
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)


# Loglama ayarları
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Metadata'yı tanıtıyoruz (Alembic tabloları buradan okur)
target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name == 'spatial_ref_sys':
        return False
    return True

def run_migrations_offline() -> None:
    """Offline modda migrationları çalıştır."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object,
        dialect_opts={"paramstyle": "named"},
        # PostGIS için render_as_batch genelde gerekmez ama SQLite için gerekirdi
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Online modda (veritabanına bağlı) migrationları çalıştır."""
    # DATABASE_URL'i env'den veya config'den dinamik alabilirsiniz
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
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