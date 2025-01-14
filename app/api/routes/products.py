from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from uuid import UUID

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, AllProductResponse
from app.api.dependencies import get_db, get_current_product
from app.db.models import Product

router = APIRouter()

@router.get("/", response_model=AllProductResponse)
async def list_products(db: AsyncSession = Depends(get_db)):
    products = await ProductRepository(db).get_all_products()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    current_product: Product = Depends(get_current_product), 
    db: AsyncSession = Depends(get_db)
    ):
    
    return current_product

@router.post("/", response_model=ProductResponse)
async def create_product(product_data: ProductCreate, db: AsyncSession = Depends(get_db)):
    product = Product(
        name=product_data.name,
        description=product_data.description,
        image=product_data.image,
    )
    return await ProductRepository(db).create_product(product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_data: ProductUpdate, 
    current_product: Product = Depends(get_current_product), 
    db: AsyncSession = Depends(get_db)
    ):
    
    updates = product_data.model_dump(exclude_unset=True)
    return await ProductRepository(db).update_product(current_product, updates)


@router.delete("/{product_id}")
async def delete_product(
    current_product: Product = Depends(get_current_product), 
    db: AsyncSession = Depends(get_db)
):
    await ProductRepository(db).delete_product(current_product)

