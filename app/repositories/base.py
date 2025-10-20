from typing import Any, Generic, Type, TypeVar

from sqlalchemy.orm import Session


ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model

    def get(self, db: Session, id_: Any) -> ModelT | None:
        return db.get(self.model, id_)

    def create(self, db: Session, obj_in: dict) -> ModelT:
        obj = self.model(**obj_in)
        db.add(obj)
        db.flush()
        return obj
