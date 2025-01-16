from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID

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
            .where(Category.id == category_id))
        category = result.unique().scalar_one_or_none()
        return category
    
    # async def get_category_by_name(self, category_name: str) -> Category | None:
    #     result = await self.db.execute(select(Category).where(Category.name == category_name))
    #     category = result.scalar_one_or_none()
    #     return category

    async def create_category(self, category: Category):
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
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

    