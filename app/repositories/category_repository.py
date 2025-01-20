from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List

from app.db.models import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_categories(self):
        result = await self.db.execute(
            select(Category)
            .options(joinedload(Category.objects))
        )
        return result.unique().scalars().all()

    async def get_category_by_id(self, category_id: UUID) -> Category | None:
        result = await self.db.execute(
            select(Category)
            .options(joinedload(Category.objects))
            .options(joinedload(Category.children))
            .where(Category.id == category_id))
        category = result.unique().scalar_one_or_none()
        return category
    
    async def get_category_by_ids(self, category_ids: list[UUID]) -> List[Category] | None:
        result = await self.db.execute(
            select(Category)
            .options(joinedload(Category.objects))
            .options(joinedload(Category.children))
            .where(Category.id.in_(category_ids)))
        category = result.unique().scalars().all()
        return category
    

    async def create_category(self, category: Category):
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)

        # Предварительная загрузка родительской категории
        await self.db.execute(
            select(Category).options(
                joinedload(Category.parent),
                joinedload(Category.parent)
            )
            .where(Category.id == category.id)
        )
        return category

    async def update_category(self, category: Category, updates: dict):
        for key, value in updates.items():
            setattr(category, key, value)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete_category(self, category: Category):
        await self.db.delete(category)
        await self.db.commit()

    
    async def get_all_categories_with_relationships(self):
        result = await self.db.execute(
            select(Category)
            .options(
                joinedload(Category.children), # Предзагрузка дочерних категорий
                joinedload(Category.objects)  # Предзагрузка дочерних категорий

            )
        )
        return result.unique().scalars().all()
    