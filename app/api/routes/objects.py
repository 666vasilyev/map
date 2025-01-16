import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.object_repository import ObjectRepository
from app.repositories.association_repository import AssociationRepository
from app.repositories.category_repository import CategoryRepository

from app.schemas.object import ObjectCreate, ObjectResponse, ObjectUpdate, AllObjectsResponse
from app.api.dependencies import get_db, get_current_object
from app.db.models import Object, Category

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
    else:
        return AllObjectsResponse(objects=objects)

@router.get("/{object_id}", response_model=ObjectResponse)
async def get_object_by_id(
    current_object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
    ):
    return current_object

@router.post("/", response_model=ObjectResponse)
async def create_object(object_data: ObjectCreate, db: AsyncSession = Depends(get_db)):

    category_db = await CategoryRepository(db).get_category_by_name(category_name=object_data.category)

    if not category_db:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current category not found"
        )

    object = Object(**object_data.model_dump())
    object_db = await ObjectRepository(db).create_object(object)


    await AssociationRepository(db).create_association(
        object_id=object_db.id,
        category_id=category_db.id
    )
    
    return object_db


@router.put("/{object_id}", response_model=ObjectResponse)
async def update_object(
    object_data: ObjectUpdate, 
    current_object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
    ):

    updates = object_data.model_dump(exclude_unset=True)

    if object_data.category:
        category = Category(name=object_data.category)

        await CategoryRepository(db).create_category(category)

        category_db = await CategoryRepository(db).create_category(category)

        await AssociationRepository(db).delete_association_from_object(current_object.id)

        await AssociationRepository(db).create_association(
            object_id=current_object.id,
            category_id=category_db.id
        )

    return await ObjectRepository(db).update_object(current_object, updates)


@router.delete("/{object_id}")
async def delete_object(
    current_object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
    ):
    await ObjectRepository(db).delete_object(current_object)
    await AssociationRepository(db).delete_association_from_object(current_object.id)


