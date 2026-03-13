from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Çevresel değişkenlerden alalım, yoksa default'a düşelim
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@localhost:5432/navi_marine"
)

# PostGIS ile çalışırken async motoru
engine = create_async_engine(DATABASE_URL, echo=True)

# Oturum fabrikası
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Model sınıflarının türetileceği Base
Base = declarative_base()

# Dependency Injection için session fonksiyonu
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()