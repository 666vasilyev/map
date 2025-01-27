import shutil
import os

from fastapi import APIRouter, UploadFile, File, status, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_repository import ProductRepository
from app.repositories.product_category_association_repository import AssociationRepository
from app.repositories.category_repository import CategoryRepository

from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, AllProductResponse, ProductIds
from app.schemas.filter import FilterModel
from app.db.models import Product
from app.api.dependencies import get_db, get_current_product, get_current_project
from app.api.routes.utils import collect_filtered_products
from app.core.settings import settings


router = APIRouter()

@router.get("/", response_model=AllProductResponse)
async def list_products(db: AsyncSession = Depends(get_db)):
    products = await ProductRepository(db).get_all_products()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
    return AllProductResponse(products=products)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    current_product: Product = Depends(get_current_product), 
    db: AsyncSession = Depends(get_db)
    ):
    
    return current_product

@router.post("/ids", response_model=AllProductResponse)
async def get_product_by_ids(
    product_ids: ProductIds,
    db: AsyncSession = Depends(get_db)
    ):

    products = await ProductRepository(db).get_products_by_ids(product_ids.ids)
    return AllProductResponse(products=products)

@router.post("/", response_model=ProductResponse)
async def create_product(product_data: ProductCreate, db: AsyncSession = Depends(get_db)):

    categories = await CategoryRepository(db).get_category_by_ids(product_data.categories)

    if len(categories) < len(product_data.categories):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not all categories exist")
    
    product = Product(
        name=product_data.name,
        description=product_data.description,
        image=product_data.image,
        country=product_data.country,
    )

    product = await ProductRepository(db).create_product(product)

    for category_id in product_data.categories:
        await AssociationRepository(db).create_association(
            product_id=product.id,
            category_id=category_id
        )

    return product

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
    db: AsyncSession = Depends(get_db),
    ):
    
    await ProductRepository(db).delete_product(current_product)
    return {"detail": "Product deleted"}


@router.post("/project/{project_id}/filtered", response_model=AllProductResponse)
async def get_filtered_products_by_project(
    filters: FilterModel,
    current_project: Product = Depends(get_current_project),
    db: AsyncSession = Depends(get_db)
):

    # Получаем категории, связанные с проектом
    category_ids = [assoc.category_id for assoc in current_project.categories]
    categories = await CategoryRepository(db).get_category_by_ids(category_ids)

    # Рекурсивно собираем продукты
    filtered_products = []
    for category in categories:
        filtered_products.extend(collect_filtered_products(category, filters))

    return AllProductResponse(products=filtered_products)


@router.post("/products/{product_id}/image", status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    file: UploadFile = File(...),
    product: Product = Depends(get_current_product),
    db: AsyncSession = Depends(get_db)
):
    """
    Загрузка изображения для продукта.
    """
    # Создаем путь для хранения файла
    product_dir = os.path.join(settings.STORAGE_DIR, "products", str(product.id))
    os.makedirs(product_dir, exist_ok=True)
    file_path = os.path.join(product_dir, "image.jpg")

    # Сохраняем файл
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Обновляем запись в базе данных
    await ProductRepository(db).update_image(product, file_path)
    return {"detail": "Image uploaded successfully", "path": file_path}



@router.delete("/products/{product_id}/image", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    product: Product = Depends(get_current_product),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление изображения продукта.
    """
    # Удаляем файл
    if os.path.exists(product.image):
        os.remove(product.image)

    # Обновляем запись в базе данных
    await ProductRepository(db).update_image(product, None)

    return {"detail": "Product image deleted successfully"}



@router.get("/products/{product_id}/image", response_class=FileResponse)
async def get_product_image(
    current_product: Product = Depends(get_current_product),
):
    """
    Получить изображение продукта по его ID.
    """
    if not current_product.image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found for the product")
    
    image_path = settings.STORAGE_DIR / "products" / str(current_product.id) / current_product.image
    if not image_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file not found")
    
    return FileResponse(image_path, media_type="image/jpeg")
