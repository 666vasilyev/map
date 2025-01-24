import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from typing import List

from app.db.models import ProductCategoryAssociation

class AssociationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_association_by_id(self, association_id: uuid.UUID) -> ProductCategoryAssociation:
        result = await self.db.execute(
            select(ProductCategoryAssociation).where(ProductCategoryAssociation.id == association_id)
        )
        association = result.scalar_one_or_none()
        if not association:
            raise NoResultFound(f"Association with id {association_id} not found")
        return association

    async def get_association_by_ids(self, association_ids: list[uuid.UUID]) -> List[ProductCategoryAssociation]:
        result = await self.db.execute(
            select(ProductCategoryAssociation).where(ProductCategoryAssociation.id.in_(association_ids))
        )
        return result.scalars().all()
    

    async def get_associations_by_product(self, object_id: uuid.UUID) -> List[ProductCategoryAssociation]:
        result = await self.db.execute(
            select(ProductCategoryAssociation)
            .options(
                joinedload(ProductCategoryAssociation.product),
                joinedload(ProductCategoryAssociation.category)
            )
            .where(ProductCategoryAssociation.product_id == object_id)
        )
        return result.scalars().all()

    async def get_associations_by_category(self, category_id: uuid.UUID) -> List[ProductCategoryAssociation]:
        result = await self.db.execute(
            select(ProductCategoryAssociation)
            .options(
                joinedload(ProductCategoryAssociation.product),  # Предзагрузка связанного объекта
                joinedload(ProductCategoryAssociation.category)  # Предзагрузка связанной категории
            )
            .where(ProductCategoryAssociation.category_id == category_id)
        )
        return result.scalars().all()


    async def create_association(self, product_id: uuid.UUID, category_id: uuid.UUID) -> ProductCategoryAssociation:
        association = ProductCategoryAssociation(product_id=product_id, category_id=category_id)
        self.db.add(association)
        await self.db.commit()
        await self.db.refresh(association)
        return association

    async def delete_association(self, association) -> None:
        await self.db.delete(association)
        await self.db.commit()

