import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.repositories.association_repository import AssociationRepository

from app.schemas.association import AssociationCreate, AssociationResponse, AssociationsByObjectResponse, AssociationsByCategoryResponse
from app.schemas.object import ObjectResponse
from app.schemas.category import CategoryResponse

from app.api.dependencies import get_db

router = APIRouter()

logging.basicConfig(level=logging.INFO)

@router.post("/", response_model=AssociationResponse)
async def create_association(association_data: AssociationCreate, db: AsyncSession = Depends(get_db)):
    return await AssociationRepository(db).create_association(
        object_id=association_data.object_id, category_id=association_data.category_id
    )

@router.get("/by-object/{object_id}", response_model=AssociationsByObjectResponse)
async def get_associations_by_object(object_id: UUID, db: AsyncSession = Depends(get_db)):
    associations = await AssociationRepository(db).get_associations_by_object(object_id)
    if not associations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No associations found for the given object"
        )
    object_data = ObjectResponse(
        id=associations[0].object_id,
        name=associations[0].object.name,
        x=associations[0].object.x,
        y=associations[0].object.y,
        ownership=associations[0].object.ownership,
        category=associations[0].object.category,
        area=associations[0].object.area,
        status=associations[0].object.status,
        links=associations[0].object.links,
        icon=associations[0].object.icon,
        image=associations[0].object.image,
        file_storage=associations[0].object.file_storage,
        description=associations[0].object.description,
    )
    categories = [
        CategoryResponse(id=assoc.category_id, name=assoc.category.name)
        for assoc in associations
    ]
    return {"object": object_data, "categories": categories}

@router.get("/by-category/{category_id}", response_model=AssociationsByCategoryResponse)
async def get_associations_by_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    associations = await AssociationRepository(db).get_associations_by_category(category_id)
    if not associations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No associations found for the given category"
        )
    category_data = CategoryResponse(
        id=associations[0].category_id,
        name=associations[0].category.name,
    )
    objects = [
        ObjectResponse(
            id=assoc.object_id,
            name=assoc.object.name,
            x=assoc.object.x,
            y=assoc.object.y,
            ownership=assoc.object.ownership,
            category=assoc.object.category,
            area=assoc.object.area,
            status=assoc.object.status,
            links=assoc.object.links,
            icon=assoc.object.icon,
            image=assoc.object.image,
            file_storage=assoc.object.file_storage,
            description=assoc.object.description,
        )
        for assoc in associations
    ]
    return {"category": category_data, "objects": objects}