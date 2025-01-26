from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.repositories.chain_repository import ChainRepository
from app.repositories.object_repository import ObjectRepository
from app.repositories.product_repository import ProductRepository

from app.schemas.chain import ChainCreate, ChainResponse, AllChainResponse, ChainUpdate, ChainsByProductResponse
from app.schemas.object import ObjectChainResponse, AllObjectChainResponse
from app.db.models import Chain
from app.api.dependencies import get_db, get_current_chain
from app.api.routes.utils import map_objects

router = APIRouter()

@router.get("/", response_model=AllChainResponse)
async def list_chains(db: AsyncSession = Depends(get_db)):
    chains = await ChainRepository(db).get_all_chains()
    if not chains:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No chains found"
        )
    else:
        return AllChainResponse(chains=chains)
    

@router.get("/{chain_id}", response_model=ChainResponse)
async def get_chain_by_id(current_chain: Chain = Depends(get_current_chain), db: AsyncSession = Depends(get_db)):
    return current_chain

@router.get("/by-product/{product_id}", response_model=ChainsByProductResponse)
async def get_chains_by_product_id(product_id: UUID, db: AsyncSession = Depends(get_db)):
    # Убедиться, что продукт существует
    product = await ProductRepository(db).get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Получить цепочки для продукта
    chains = await ChainRepository(db).get_chains_by_product_id(product_id)
    return {"product_id": product_id, "chains": chains}


@router.get("/objects/by_product/{product_id}", response_model=AllObjectChainResponse)
async def get_object_by_product_id(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
    ):

    objects = await ChainRepository(db).get_objects_by_product_id(product_id)
    if not objects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No objects found for this product"
        )
    
    objects_to_return = map_objects(objects, product_id)
    return AllObjectChainResponse(objects=objects_to_return)



@router.post("/", response_model=ChainResponse)
async def create_chain(chain_data: ChainCreate, db: AsyncSession = Depends(get_db)):

    # TODO: сделать обработчик ошибки для каждого объекта
    objects = await ObjectRepository(db).get_object_by_ids(
        [
            chain_data.source_object_id,
            chain_data.target_object_id
        ]
    )

    if len(objects) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source or target object not found"
        )

    chain = Chain(
        source_object_id=chain_data.source_object_id,
        target_object_id=chain_data.target_object_id,
        product_id=chain_data.product_id
    )
    return await ChainRepository(db).create_chain(chain)

@router.put("/{chain_id}", response_model=ChainResponse)
async def update_chain(
    chain_data: ChainUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_chain: Chain = Depends(get_current_chain)
    ):

    updates = chain_data.model_dump(exclude_unset=True)
    return await ChainRepository(db).update_chain(current_chain, updates)
        
@router.delete("/{chain_id}")
async def delete_chain(
    db: AsyncSession = Depends(get_db),
    current_chain: Chain = Depends(get_current_chain)
    ):

    await ChainRepository(db).delete_chain(current_chain)

