from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List

from app.db.models import Product
from app.core.settings import settings

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = settings

    async def get_all_products(self):
        result = await self.db.execute(select(Product))
        return result.scalars().all()

    async def get_product_by_id(self, product_id: UUID):
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        return product
    
    async def get_products_by_ids(self, ids: List[UUID]):
        result = await self.db.execute(select(Product).where(Product.id.in_(ids)))
        return result.scalars().all()

    async def create_product(self, product: Product):
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update_product(self, product: Product, updates: dict):
        for key, value in updates.items():
            setattr(product, key, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete_product(self, product: Product):
        await self.db.delete(product)
        await self.db.commit()

    async def update_image(self, product: Product) -> Product:
        """
        Обновляет путь к изображению для продукта.
        """
        product.image = f'{settings.API_URL}/products/{product.id}/image'
        await self.db.commit()
        await self.db.refresh(product)
        return product