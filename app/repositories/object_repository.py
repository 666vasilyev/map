from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List

from app.db.models import Object

class ObjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_objects(self) -> List[Object]:
        result = await self.db.execute(
            select(Object)
    )
        return result.unique().scalars().all()

    async def get_object_by_id(self, object_id: UUID) -> Object:
        result = await self.db.execute(
            select(Object)
            .where(Object.id == object_id))
        obj = result.unique().scalar_one_or_none()
        return obj
    
    async def get_object_by_ids(self, object_ids: list[UUID]) -> List[Object]:
        result = await self.db.execute(
            select(Object)
            .where(Object.id.in_(object_ids)))
        objects = result.unique().scalars().all()
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

    async def update_image(self, obj: Object, image_path: str| None) -> Object:
        """
        Обновляет путь к изображению для объекта.
        """
        obj.image = image_path
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update_file_storage(self, obj: Object, file_storage_path: str | None) -> Object:
        """
        Обновляет путь к файловому хранилищу для объекта.
        """
        obj.file_storage = file_storage_path
        await self.db.commit()
        await self.db.refresh(obj)
        return obj