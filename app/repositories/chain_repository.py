from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List

from app.db.models import Chain, Object

class ChainRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_chains(self):
        result = await self.db.execute(select(Chain))
        return result.unique().scalars().all()

    async def get_chain_by_id(self, chain_id: UUID):
        result = await self.db.execute(select(Chain).where(Chain.id == chain_id))
        return result.unique().scalar_one_or_none()
    
    async def get_chains_by_product_id(self, product_id: UUID) -> List[Chain]:
        result = await self.db.execute(
            select(Chain)
            .where((Chain.product_id == product_id))
        )
        return result.unique().scalars().all()
    
    async def get_objects_by_product_id(self, product_id: UUID) -> List[Object]:
        """
        Получает список объектов, связанных с продуктом через цепочки.
        
        :param product_id: UUID продукта
        :return: Список объектов (List[Object])
        """
        result = await self.db.execute(
            select(Object)
            .join(Chain, (Chain.source_object_id == Object.id) | (Chain.target_object_id == Object.id))
            .where(Chain.product_id == product_id)
            .options(joinedload(Object.products), joinedload(Object.chains_source))
        )
        return result.unique().scalars().all()

    async def create_chain(self, chain: Chain):
        self.db.add(chain)
        await self.db.commit()
        await self.db.refresh(chain)
        return chain

    async def update_chain(self, chain: Chain, updates: dict):

        for key, value in updates.items():
            setattr(chain, key, value)
        await self.db.commit()
        await self.db.refresh(chain)
        return chain

    async def delete_chain(self, chain: Chain):
        await self.db.delete(chain)
        await self.db.commit()