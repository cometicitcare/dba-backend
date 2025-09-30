import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services.user_service import user_service


async def seed():
    async with AsyncSessionLocal() as db: # type: AsyncSession
        await user_service.create_user(
            db,
            user_id="admin0001",
            username="admin",
            email="admin@example.com",
            password="Admin@123",
        )
    await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())