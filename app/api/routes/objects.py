import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.object_repository import ObjectRepository
from app.schemas.object import ObjectUpdate, ObjectResponse, ObjectCreate, AllObjectsResponse
from app.api.dependencies import get_db, get_current_object
from app.db.models import Object

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
        description=object_data.description
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


