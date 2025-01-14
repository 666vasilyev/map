import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from app.db.models import ObjectCategoryAssociation

class AssociationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_association_by_id(self, association_id: uuid.UUID) -> ObjectCategoryAssociation:
        result = await self.db.execute(
            select(ObjectCategoryAssociation).where(ObjectCategoryAssociation.id == association_id)
        )
        association = result.scalar_one_or_none()
        if not association:
            raise NoResultFound(f"Association with id {association_id} not found")
        return association

    async def get_associations_by_object(self, object_id: uuid.UUID) -> list[ObjectCategoryAssociation]:
        result = await self.db.execute(
            select(ObjectCategoryAssociation).where(ObjectCategoryAssociation.object_id == object_id)
        )
        return result.scalars().all()

    async def get_associations_by_category(self, category_id: uuid.UUID) -> list[ObjectCategoryAssociation]:
        result = await self.db.execute(
            select(ObjectCategoryAssociation).where(ObjectCategoryAssociation.category_id == category_id)
        )
        return result.scalars().all()

    async def create_association(self, object_id: uuid.UUID, category_id: uuid.UUID) -> ObjectCategoryAssociation:
        association = ObjectCategoryAssociation(object_id=object_id, category_id=category_id)
        self.db.add(association)
        await self.db.commit()
        await self.db.refresh(association)
        return association

    async def delete_association(self, association_id: uuid.UUID) -> None:
        association = await self.get_association_by_id(association_id)
        await self.db.delete(association)
        await self.db.commit()
    async def delete_association_from_object(self, object_id: uuid.UUID) -> None:
        association = await self.get_associations_by_object(object_id)
        await self.db.delete(association)
        await self.db.commit()