from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from uuid import UUID

from app.db.session import async_session
from app.repositories.chain_repository import ChainRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.object_repository import ObjectRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.association_repository import AssociationRepository

from app.db.models import Chain, Category, Object, Product, ObjectCategoryAssociation


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def get_current_chain(chain_id: UUID, db: AsyncSession = Depends(get_db)):
    current_chain = await ChainRepository(db).get_chain_by_id(chain_id)
    if not current_chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chain not found"
        )
    else:
        return current_chain
    
async def get_current_category(category_id: UUID, db: AsyncSession = Depends(get_db)) -> Category:
    current_category = await CategoryRepository(db).get_category_by_id(category_id)
    if not current_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    else:
        return current_category
    
async def get_current_object(object_id: UUID, db: AsyncSession = Depends(get_db)):
    current_object = await ObjectRepository(db).get_object_by_id(object_id)
    if not current_object:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Object not found"
        )
    else:
        return current_object
    

async def get_current_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    current_product = await ProductRepository(db).get_product_by_id(product_id)
    if not current_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    else:
        return current_product
    
async def get_current_association(association_id: UUID, db: AsyncSession = Depends(get_db)):
    current_association = await AssociationRepository(db).get_association_by_id(association_id)
    if not current_association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Association not found"
        )
    else:
        return current_association
