from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from uuid import UUID
from typing import List

from app.db.models import Object
from app.core.settings import settings

class ObjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = settings

    async def get_all_objects(self) -> List[Object]:
        result = await self.db.execute(
            select(Object)
            .options(selectinload(Object.branches))
    )
        return result.unique().scalars().all()

    async def get_object_by_id(self, object_id: UUID) -> Object:
        result = await self.db.execute(
            select(Object)
            .options(selectinload(Object.branches))
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

        # Делаем дополнительный запрос на загрузку филиалов с помощью selectinload
        query = select(Object).options(selectinload(Object.branches)).where(Object.id == obj.id)
        result = await self.db.execute(query)

        return result.unique().scalar_one_or_none()

    async def update_object(self, obj: Object, updates: dict) -> Object:
        for key, value in updates.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete_object(self, obj: Object):
        await self.db.delete(obj)
        await self.db.commit()

    async def update_image(self, obj: Object) -> Object:
        """
        Обновляет путь к изображению для объекта.
        """
        obj.image = f'{settings.API_URL}/objects/{obj.id}/image'
        await self.db.commit()
        await self.db.refresh(obj)
        
        # Делаем дополнительный запрос на загрузку филиалов с помощью selectinload
        query = select(Object).options(selectinload(Object.branches)).where(Object.id == obj.id)
        result = await self.db.execute(query)

        return result.unique().scalar_one_or_none()

    async def update_file_storage(self, obj: Object, file_storage: List[str] | None) -> Object:
        """
        Обновляет путь к файловому хранилищу для объекта.
        """
        obj.file_storage = obj.file_storage + file_storage
        await self.db.commit()
        await self.db.refresh(obj)

        # Делаем дополнительный запрос на загрузку филиалов с помощью selectinload
        query = select(Object).options(selectinload(Object.branches)).where(Object.id == obj.id)
        result = await self.db.execute(query)

        return result.unique().scalar_one_or_none()
    
    
    async def get_objects_within_bounds(self, x: float, y: float, project_id: UUID) -> List[Object]:
        """Получить объекты в квадрате с центром (x, y) и радиусом 1 км."""
        result = await self.db.execute(
            select(Object)
            .options(selectinload(Object.branches))
            .where(
                (Object.x >= x - 1.0) & (Object.x <= x + 1.0),
                (Object.y >= y - 1.0) & (Object.y <= y + 1.0),
                Object.project_id == project_id
            )
        )
        return result.unique().scalars().all()
    

    async def remove_file_from_storage(self, obj: Object, file_name: str) -> Object:
        """
        Удаляет из file_storage объекта элемент с указанным именем файла.
        
        :param obj: Экземпляр объекта, у которого нужно удалить файл из file_storage.
        :param file_name: Имя файла, которое необходимо удалить из file_storage.
        :return: Обновленный объект.
        """
        if obj.file_storage:
            # Если файл присутствует в списке, удаляем его
            if file_name in obj.file_storage:
                obj.file_storage = [f for f in obj.file_storage if f != file_name]
            else:
                # Если файл не найден, можно либо ничего не делать, либо вызвать исключение
                raise Exception(f"File '{file_name}' not found in file_storage.")
        else:
            raise Exception("File storage is empty or not set for this object.")

        await self.db.commit()
        await self.db.refresh(obj)

        # Дополнительный запрос для загрузки филиалов
        query = select(Object).options(selectinload(Object.branches)).where(Object.id == obj.id)
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
