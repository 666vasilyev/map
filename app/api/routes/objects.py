import logging
import shutil
import os
import uuid
import json

from fastapi import APIRouter, UploadFile, File, status, Depends, HTTPException, Form
from fastapi.responses import FileResponse
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.object_repository import ObjectRepository
from app.schemas.object import (
    ObjectUpdate, 
    ObjectResponse, 
    ObjectCreate, 
    AllObjectsResponse, 
    LocationCheckRequest, 
    AllSmallObjectsResponse, 
    ObjectSmallResponse
)
from app.schemas.enums import StatusEnum

from app.api.dependencies import get_db, get_current_object
from app.db.models import Object
from app.core.settings import settings
from app.api.routes.utils import attach_files_to_object, attach_image_to_object

router = APIRouter()

logging.basicConfig(level=logging.INFO)

@router.get("/", response_model=AllObjectsResponse)
async def list_objects(db: AsyncSession = Depends(get_db)):
    objects = await ObjectRepository(db).get_all_objects()
    if not objects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No objects found"
        )
    objects_to_return = [ObjectResponse.model_validate(object) for object in objects]

    return AllObjectsResponse(objects=objects_to_return)

@router.get("/{object_id}", response_model=ObjectResponse)
async def get_object_by_id(
    current_object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
    ):

    return current_object

@router.post("/", response_model=ObjectResponse)
async def create_object(
    x: float = Form(...),
    y: float = Form(...),
    name: str = Form(...),
    ownership: Optional[str] = Form(None),
    area: float = Form(...),
    object_status: StatusEnum = Form(...),
    links: Optional[str] = Form(None),
    icon: Optional[str] = Form(None),
    image: UploadFile = File(None),
    files: List[UploadFile] = File(None),
    description: Optional[str] = Form(None),
    parent_id: Optional[uuid.UUID] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новый объект. Если указан `parent_id`, объект будет филиалом. 
    Также можно сразу загрузить изображение и файлы.
    """

    # TODO: сделать валидацию ссылок до HttpUrl
    # Преобразуем `links` в список, если передана строка
    if links:
        try:
            links = json.loads(links) if links.startswith("[") else links.split(",")
            links = [link.strip() for link in links]  # Очистка пробелов
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid JSON format for links"
                )

    # Проверка наличия родительского объекта, если указан parent_id
    parent_object = None
    if parent_id:
        parent_object = await ObjectRepository(db).get_object_by_id(parent_id)
        if not parent_object:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent object with ID {parent_id} not found"
            )

    obj = Object(
        x=x,
        y=y,
        name=name,
        ownership=ownership,
        area=area,
        status=object_status.value,
        links=links,
        icon=icon,
        image=False,  # Обновится позже, если передано изображение
        file_storage=[],  # Обновится позже, если загружены файлы
        description=description,
        parent_id=parent_id
    )

    object_db = await ObjectRepository(db).create_object(obj)

    # Загружаем изображение, если передано
    if image:
        object_db = await attach_image_to_object(db, object_db, image)

    # Загружаем файлы, если переданы
    if files:
        object_db = await attach_files_to_object(db, object_db, files)

    return object_db


@router.put("/{object_id}", response_model=ObjectResponse)
async def update_object(
    object_data: str = Form("{}"),  # Принимаем JSON как строку
    files: List[UploadFile] = File(None),
    image: UploadFile = File(None),
    current_object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление объекта. Можно передать новые данные (object_data), а также загрузить файлы и изображение.
    """
    try:
        object_data_dict = json.loads(object_data)  # Разбираем JSON-строку в объект Python
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="Invalid JSON format in object_data"
            )

    # Обновляем объект, если переданы данные
    updated_object = await ObjectRepository(db).update_object(current_object, object_data_dict)

    # Загружаем изображение, если передано
    if image:
        updated_object = await attach_image_to_object(db, updated_object, image)

    # Загружаем файлы, если переданы
    if files:
        updated_object = await attach_files_to_object(db, updated_object, files)

    return ObjectResponse.model_validate(updated_object)


@router.delete("/{object_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object(
    current_object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаляет объект вместе со всеми его файлами и изображениями.
    """
    object_dir = os.path.join(settings.STORAGE_DIR, "objects", str(current_object.id))

    # Удаляем папку с файлами, если существует
    if os.path.exists(object_dir) and os.path.isdir(object_dir):
        shutil.rmtree(object_dir)  # Полностью удаляем папку с объектом

    # Удаляем объект из базы данных
    await ObjectRepository(db).delete_object(current_object)



@router.post("/{object_id}/image", status_code=status.HTTP_201_CREATED)
async def upload_object_image(
    file: UploadFile = File(...),
    object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Загрузка изображения для объекта.
    """
    await attach_image_to_object(db, object, file)
    return {"detail": "Image uploaded successfully"}


@router.post("/{object_id}/files", status_code=status.HTTP_201_CREATED)
async def upload_object_files(
    files: List[UploadFile] = File(...),
    object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Загрузка документов для объекта.
    """
    obj = await attach_files_to_object(db, object, files)
    return {"files": obj.file_storage}



@router.delete("/{object_id}/image", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object_image(
    obj: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление изображения объекта.
    """

    # Удаляем файл
    if os.path.exists(obj.image):
        os.remove(obj.image)

    # Обновляем запись в базе данных
    await ObjectRepository(db).update_image(obj, None)
    return {"detail": "Object image deleted successfully"}


@router.delete("/{object_id}/files", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object_files(
    obj: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление всех файлов объекта.
    """

    # Удаляем папку с файлами
    if os.path.exists(obj.file_storage):
        shutil.rmtree(obj.file_storage)

    # Обновляем запись в базе данных
    await ObjectRepository(db).update_file_storage(obj, None)

    return {"detail": "Object files deleted successfully"}



@router.get("/{object_id}/image", response_class=FileResponse)
async def get_object_image(
    current_object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить изображение объекта по его ID.
    """
    if not current_object.image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found for the object")
    
    image_path = settings.STORAGE_DIR / "objects" / str(current_object.id) / "image.jpg"
    if not image_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file not found")
    
    return FileResponse(image_path, media_type="image/jpeg")


@router.get("/{object_id}/files")
async def get_object_files(
    current_object: Object = Depends(get_current_object),
):
    """
    Получить список всех файлов, связанных с объектом по его ID.
    """
    if not current_object.file_storage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File storage not found for the object")
    
    # Path to the files directory
    files_dir = settings.STORAGE_DIR / "objects" / str(current_object.id) / "files"
    
    if not files_dir.exists() or not files_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Files directory not found")

    # Collect all file names in the directory
    file_list = [file.name for file in files_dir.iterdir() if file.is_file()]
    
    if not file_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No files found for the object")
    
    return {"files": file_list}


@router.get("/{object_id}/files/{file_name}", response_class=FileResponse)
async def get_object_file(
    file_name: str,
    current_object: Object = Depends(get_current_object),
):
    """
    Получить файл из файлового хранилища объекта по его ID.
    """
    if not current_object.file_storage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File storage not found for the object")
    
    file_path = settings.STORAGE_DIR / "objects" / str(current_object.id) / "files" / file_name
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    return FileResponse(file_path, media_type="application/octet-stream", filename=file_name)

@router.post("/check_location", response_model=AllSmallObjectsResponse)
async def check_location(
    location: LocationCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Проверить наличие объектов в квадрате с центром в указанных координатах и радиусом 1 км.
    """
    objects = await ObjectRepository(db).get_objects_within_bounds(location.x, location.y)

    if not objects:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Objects in current location not found")
    
    return AllSmallObjectsResponse(
        objects=[ObjectSmallResponse.model_validate(obj) for obj in objects]
    )