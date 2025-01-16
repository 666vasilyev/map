from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List

from app.db.models import Object

class ObjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_objects(self) -> List[Object]:
        result = await self.db.execute(select(Object))
        return result.scalars().all()

    async def get_object_by_id(self, object_id: UUID) -> Object:
        result = await self.db.execute(
            select(Object)
            .options(joinedload(Object.categories))
            .where(Object.id == object_id))
        obj = result.unique().scalar_one_or_none()
        return obj
    
    async def get_object_by_ids(self, object_ids: list[UUID]) -> List[Object]:
        result = await self.db.execute(
            select(Object)
            .where(Object.id.in_(object_ids)))
        objects = result.scalars().all()
        return objects

    async def create_object(self, obj: Object) -> Object:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update_object(self, obj: Object, updates: dict) -> Object:
        for key, value in updates.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete_object(self, obj: Object):
        await self.db.delete(obj)
        await self.db.commit()
