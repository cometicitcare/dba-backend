from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True)


AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, autoflush=False, autocommit=False
)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session