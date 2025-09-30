from typing import TypeVar, Generic, Type, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model


async def get(self, db: AsyncSession, id_: Any) -> ModelT | None:
    stmt = select(self.model).where(self.model.__table__.primary_key.columns.values()[0] == id_)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def create(self, db: AsyncSession, obj_in: dict) -> ModelT:
    obj = self.model(**obj_in)
    db.add(obj)
    await db.flush()
    return obj