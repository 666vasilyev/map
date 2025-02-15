import os
import aiofiles

from typing import List, Optional
from uuid import UUID
from fastapi import UploadFile, HTTPException, status

from app.schemas.tree import TreeResponse
from app.schemas.product import ProductResponse
from app.schemas.filter import FilterModel
from app.schemas.object import ObjectCoordinates, ObjectChainResponse, AllObjectChainResponse
from app.db.models import Category, Product, Object
from app.core.settings import settings
from app.repositories.object_repository import ObjectRepository


def map_all_category(category: Category) -> TreeResponse:

    products = [ProductResponse.model_validate(product.product) for product in category.products]

    return TreeResponse(
        id=category.id,
        name=category.name,
        objects=[map_all_category(child) for child in category.children] + products
        )

def apply_filters(products: List[Product], filters: FilterModel) -> List[Product]:
    """
    Применяет фильтры к продуктам.
    """
    def matches(product: Product) -> bool:
        return all([
            filters.name is None or filters.name in product.name,
            filters.description is None or (product.description and filters.description in product.description),
            filters.image is None or (product.image and filters.image in product.image),
            filters.country is None or (product.country and filters.country in product.country)
        ])

    return [product for product in products if matches(product)]


def map_category(category: Category, filters: Optional[FilterModel] = None) -> Optional[TreeResponse]:
    """
    Рекурсивно строит дерево категорий, исключая пустые категории.
    """
    # Применяем фильтры к продуктам
    products = [assoc.product for assoc in category.products]
    if filters:
        products = apply_filters(products, filters)

    # Преобразуем продукты в ответную схему
    products_response = [ProductResponse.model_validate(product) for product in products]

    # Рекурсивно обрабатываем дочерние категории
    children_response = [map_category(child, filters) for child in category.children]
    # Удаляем пустые дочерние категории
    children_response = [child for child in children_response if child is not None]

    # Если у текущей категории нет ни продуктов, ни дочерних категорий — исключаем её
    if not products_response and not children_response:
        return None

    return TreeResponse(
        id=category.id,
        name=category.name,
        objects=children_response + products_response
    )

def collect_filtered_products(category: Category, filters: Optional[FilterModel] = None) -> List[ProductResponse]:
    """
    Рекурсивно собирает продукты из категории и ее дочерних категорий, применяя фильтры.
    """
    # Получаем продукты из категории
    products = [assoc.product for assoc in category.products]

    # Применяем фильтры
    if filters:
        products = apply_filters(products, filters)

    # Конвертируем продукты в ответную схему
    products_response = [ProductResponse.model_validate(product) for product in products]

    # Рекурсивно обрабатываем дочерние категории
    for child in category.children:
        products_response.extend(collect_filtered_products(child, filters))

    return products_response


def map_objects(objects: List[Object], product_id: UUID) -> AllObjectChainResponse:
    """
    Маппит список SQLAlchemy объектов в Pydantic модели ObjectResponse.

    :param objects: Список объектов SQLAlchemy модели Object.
    :return: Список объектов Pydantic модели ObjectResponse.
    """
    mapped_objects = []

    for obj in objects:
        chains = []
        for chain in obj.chains_source:
            if chain.product_id == product_id:
                chains.append(
                    ObjectCoordinates(
                        id=chain.target_object.id,
                        x=chain.target_object.x,
                        y=chain.target_object.y,
                    )
                )
        mapped_object = ObjectChainResponse(
            x=obj.x,
            y=obj.y,
            id=obj.id,
            name=obj.name,
            icon=obj.icon,
            description=obj.description,
            chains=chains,
        )
        mapped_objects.append(mapped_object)

    return mapped_objects


async def save_uploaded_files(object_id: int, files: List[UploadFile]) -> List[str]:
    """
    Сохранение списка загруженных файлов в файловое хранилище объекта.
    
    :param object_id: ID объекта, к которому добавляются файлы.
    :param files: Список загруженных файлов.
    :return: Список путей сохраненных файлов.
    """

    # Создаем путь для хранения файлов
    object_dir = os.path.join(settings.STORAGE_DIR, "objects", str(object_id), "files")
    os.makedirs(object_dir, exist_ok=True)

    saved_files = []
    for file in files:
        file_path = os.path.join(object_dir, file.filename)

        try:
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(await file.read())
        except Exception as e:
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error saving image: {str(e)}"
            )
        
        saved_files.append(file_path)

    return saved_files


async def attach_files_to_object(db, object: Object, files: List[UploadFile]):
    """
    Загружает файлы в хранилище объекта и обновляет информацию в базе данных.
    
    :param db: Сессия базы данных.
    :param object: Экземпляр объекта.
    :param files: Список загруженных файлов.
    """
    if files:
        saved_files = await save_uploaded_files(object.id, files)
        obj = await ObjectRepository(db).update_file_storage(object, saved_files[0])
    
    return obj


async def save_uploaded_image(object_id: int, file: UploadFile) -> str:
    """
    Сохраняет загруженное изображение для объекта.

    :param object_id: ID объекта, к которому добавляется изображение.
    :param file: Загруженный файл.
    :return: Путь к сохраненному изображению.
    """
    # Создаем путь для хранения изображения
    object_dir = os.path.join(settings.STORAGE_DIR, "objects", str(object_id))
    os.makedirs(object_dir, exist_ok=True)
    file_path = os.path.join(object_dir, "image.jpg")

    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await file.read())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error saving image: {str(e)}"
            )

    return file_path


async def attach_image_to_object(db, object: Object, file: UploadFile):
    """
    Загружает изображение и обновляет информацию об объекте в базе данных.

    :param db: Сессия базы данных.
    :param object: Экземпляр объекта.
    :param file: Загруженный файл изображения.
    """
    file_path = await save_uploaded_image(object.id, file)
    obj = await ObjectRepository(db).update_image(object, file_path)
    return obj