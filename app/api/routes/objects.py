import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.object_repository import ObjectRepository
from app.repositories.association_repository import AssociationRepository
from app.repositories.category_repository import CategoryRepository

from app.schemas.object import ObjectUpdate
from app.schemas.category import CategoryResponse

from app.schemas.category_object import ObjectCreate, ObjectResponseWithCategories, AllObjectsResponse
from app.api.dependencies import get_db, get_current_object
from app.db.models import Object, Category

router = APIRouter()

logging.basicConfig(level=logging.INFO)

@router.get("/", response_model=AllObjectsResponse)
async def list_objects(db: AsyncSession = Depends(get_db)):
    objects = await ObjectRepository(db).get_all_objects()
    if objects:

        answers = []

        for object in objects:

            ids_list = [category.category_id for category in object.categories]

            ids = set(ids_list)

            categories = await CategoryRepository(db).get_category_by_ids(ids)

            object_to_return = ObjectResponseWithCategories(
                id=object.id,
                x=object.x,
                y=object.y,
                name=object.name,
                ownership=object.ownership,
                area=object.area,
                status=object.status,
                links=object.links,
                icon=object.icon,
                image=object.image,
                file_storage=object.file_storage,
                description=object.description,
                categories=[CategoryResponse.model_validate(category) for category in categories]
            )

            answers.append(object_to_return)
        return AllObjectsResponse(objects=answers)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No objects found"
        )

@router.get("/{object_id}", response_model=ObjectResponseWithCategories)
async def get_object_by_id(
    current_object: Object = Depends(get_current_object),
    db: AsyncSession = Depends(get_db)
    ):
    ids_list = [category.category_id for category in current_object.categories]
    ids = set(ids_list)
    categories = await CategoryRepository(db).get_category_by_ids(ids)
    return ObjectResponseWithCategories(
                id=current_object.id,
                x=current_object.x,
                y=current_object.y,
                name=current_object.name,
                ownership=current_object.ownership,
                area=current_object.area,
                status=current_object.status,
                links=current_object.links,
                icon=current_object.icon,
                image=current_object.image,
                file_storage=current_object.file_storage,
                description=current_object.description,
                categories=[CategoryResponse.model_validate(category) for category in categories]
            )

@router.post("/", response_model=ObjectResponseWithCategories)
async def create_object(object_data: ObjectCreate, db: AsyncSession = Depends(get_db)):

    for category_id in object_data.categories:

        category_db = await CategoryRepository(db).get_category_by_id(category_id=category_id)

        if not category_db:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
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
        description=object_data.description
    )
    object_db = await ObjectRepository(db).create_object(obj)

    for category_id in object_data.categories:
        await AssociationRepository(db).create_association(
            object_id=object_db.id,
            category_id=category_db.id
        )
    
    object_with_categories = await ObjectRepository(db).get_object_by_id(object_db.id)

    ids_list = [category.category_id for category in object_with_categories.categories]
    ids = set(ids_list)

    categories = await CategoryRepository(db).get_category_by_ids(ids)

    return ObjectResponseWithCategories(
                id=object_with_categories.id,
                x=object_with_categories.x,
                y=object_with_categories.y,
                name=object_with_categories.name,
                ownership=object_with_categories.ownership,
                area=object_with_categories.area,
                status=object_with_categories.status,
                links=object_with_categories.links,
                icon=object_with_categories.icon,
                image=object_with_categories.image,
                file_storage=object_with_categories.file_storage,
                description=object_with_categories.description,
                categories=[CategoryResponse.model_validate(category) for category in categories]
            )


@router.put("/{object_id}", response_model=ObjectResponseWithCategories)
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

    for category in current_object.categories:
        await AssociationRepository(db).delete_association(category.id)

    await ObjectRepository(db).delete_object(current_object)


