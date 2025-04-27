import os
import aiofiles
import hashlib

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
            filters.name is None or (product.name and filters.name.lower() in product.name.lower()),
            filters.description is None or (product.description and filters.description.lower() in product.description.lower()),
            filters.image is None or (product.image and filters.image.lower() in product.image.lower()),
            filters.country is None or (product.country and filters.country.lower() in product.country.lower())
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
                        chain_id=chain.id,
                        name=chain.target_object.name
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

async def file_checksum(file_path: str) -> str:
    """Вычисляет хеш-сумму (SHA256) файла для проверки идентичности."""
    hash_sha256 = hashlib.sha256()
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(8192):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


async def upload_file_checksum(file: UploadFile) -> str:
    """Вычисляет хеш-сумму загружаемого файла без его сохранения на диск."""
    hash_sha256 = hashlib.sha256()
    chunk = await file.read()
    hash_sha256.update(chunk)
    await file.seek(0)  # Сбрасываем позицию файла после чтения
    return hash_sha256.hexdigest()

async def save_uploaded_files(object_id: int, files: List[UploadFile]) -> List[str]:
    """
    Сохранение списка загруженных файлов в файловое хранилище объекта.

    Если файл с таким именем уже существует, к имени файла добавляется суффикс (1), (2) и т.д.
    
    :param object_id: ID объекта, к которому добавляются файлы.
    :param files: Список загруженных файлов.
    :return: Список имён сохранённых файлов.
    """

    # Создаем путь для хранения файлов
    object_dir = os.path.join(settings.STORAGE_DIR, "objects", str(object_id), "files")
    os.makedirs(object_dir, exist_ok=True)

    saved_files = []
    for file in files:
        base_filename = file.filename
        file_path = os.path.join(object_dir, base_filename)

        # Проверка: если файл с таким именем уже существует, генерируем новое имя
        if os.path.exists(file_path):
            existing_checksum = await file_checksum(file_path)
            new_file_checksum = await upload_file_checksum(file)

            if existing_checksum == new_file_checksum:
                # 🔴 Если файл уже есть и он идентичен - НЕ загружаем
                continue  # Пропускаем загрузку и переходим к следующему файлу

            name, ext = os.path.splitext(base_filename)
            counter = 1
            new_filename = f"{name}({counter}){ext}"
            file_path = os.path.join(object_dir, new_filename)
            while os.path.exists(file_path):
                counter += 1
                new_filename = f"{name}({counter}){ext}"
                file_path = os.path.join(object_dir, new_filename)
            base_filename = new_filename  # обновляем имя файла

        try:
            async with aiofiles.open(file_path, "wb") as f:
                # Читаем и записываем содержимое файла
                await f.write(await file.read())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error saving file: {str(e)}"
            )
        
        saved_files.append(base_filename)

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
        obj = await ObjectRepository(db).update_file_storage(object, saved_files)
    
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
    await save_uploaded_image(object.id, file)
    obj = await ObjectRepository(db).update_image(object, True)
    return obj