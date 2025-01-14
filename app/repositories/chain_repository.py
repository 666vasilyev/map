from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List

from app.db.models import Chain

class ChainRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_chains(self):
        result = await self.db.execute(select(Chain))
        return result.scalars().all()

    async def get_chain_by_id(self, chain_id: UUID):
        result = await self.db.execute(select(Chain).where(Chain.id == chain_id))
        return result.scalar_one_or_none()
    
    async def get_chains_by_product_id(self, product_id: UUID) -> List[Chain]:
        result = await self.db.execute(
            select(Chain)
            .where((Chain.product_id == product_id))
        )
        return result.scalars().all()
    

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