from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Çevresel değişkenlerden alalım, yoksa default'a düşelim
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://dbmasteruser:ec2;&=6KtFJi9#J{RE1#OC52w5STi8it@ls-a5ad1b260b195f323cd3b9091ae79e32877778de.cfyc6yasm15y.eu-central-1.rds.amazonaws.com:5432/navi_marine"
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