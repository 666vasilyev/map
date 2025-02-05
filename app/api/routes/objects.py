import logging
import shutil
import os

from fastapi import APIRouter, UploadFile, File, status, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List
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

from app.api.dependencies import get_db, get_current_object
from app.db.models import Object
from app.core.settings import settings

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
async def create_object(object_data: ObjectCreate, db: AsyncSession = Depends(get_db)):
    """
    Создать новый объект. Если указан `parent_id`, объект будет филиалом.
    """
    # Проверка наличия родительского объекта, если указан parent_id
    parent_object = None
    if object_data.parent_id:
        parent_object = await ObjectRepository(db).get_object_by_id(object_data.parent_id)
        if not parent_object:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent object with ID {object_data.parent_id} not found"
            )

    obj = Object(
        x=object_data.x,
        y=object_data.y,
        name=object_data.name,
        ownership=object_data.ownership,
        area=object_data.area,
        status=object_data.status.value,
        links=object_data.links,
        icon=object_data.icon,
        image=object_data.image,
        file_storage=object_data.file_storage,
        description=object_data.description,
        parent_id=object_data.parent_id
    )
    object_db = await ObjectRepository(db).create_object(obj)
    return object_db


@router.put("/{object_id}", response_model=ObjectResponse)
async def update_object(
    object_data: ObjectUpdate, 
    current_object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
    ):

    updates = object_data.model_dump(exclude_unset=True)

    return await ObjectRepository(db).update_object(current_object, updates)


@router.delete("/{object_id}")
async def delete_object(
    current_object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
    ):

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

    # Создаем путь для хранения файла
    object_dir = os.path.join(settings.STORAGE_DIR, "objects", str(object.id))
    os.makedirs(object_dir, exist_ok=True)
    file_path = os.path.join(object_dir, "image.jpg")

    # Сохраняем файл
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Обновляем запись в базе данных
    await ObjectRepository(db).update_image(object, file_path)

    return {"detail": "Image uploaded successfully", "path": file_path}


@router.post("/{object_id}/files", status_code=status.HTTP_201_CREATED)
async def upload_object_files(
    files: List[UploadFile] = File(...),
    object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
):
    """
    Загрузка документов для объекта.
    """

    # Создаем путь для хранения файлов
    object_dir = os.path.join(settings.STORAGE_DIR, "objects", str(object.id), "files")
    os.makedirs(object_dir, exist_ok=True)

    saved_files = []
    for file in files:
        file_path = os.path.join(object_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_files.append(file_path)

    # Обновляем запись в базе данных
    await ObjectRepository(db).update_file_storage(object, object_dir)
    return {"detail": "Files uploaded successfully", "files": saved_files}



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
    
    image_path = settings.STORAGE_DIR / "objects" / str(current_object.id) / current_object.image
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