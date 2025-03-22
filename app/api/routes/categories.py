import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.models import Category
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_category_association_repository import AssociationRepository
from app.repositories.project_category_association_repository import ProjectCategoryAssociationRepository
from app.repositories.project_repository import ProjectRepository


from app.schemas.category import (
    CategoryCreate, 
    CategoryResponse, 
    CategoryUpdate, 
    CategoryCreateV2
)

from app.api.dependencies import get_db, get_current_category

router = APIRouter()
logging.basicConfig(level=logging.INFO)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(
    db: AsyncSession = Depends(get_db),
    current_category: Category = Depends(get_current_category)
    ):

    return current_category
@router.post("/", response_model=CategoryResponse)
async def create_category(category_data: CategoryCreateV2, db: AsyncSession = Depends(get_db)):
    category = Category(
        name=category_data.name
        )


    parent_category = await CategoryRepository(db).get_category_by_id(category_data.id)
    project = await ProjectRepository(db).get_project_by_id(category_data.id)

    if not parent_category and not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent category or project not found")

    try:
        if parent_category:
            category.parent = parent_category
            category_db = await CategoryRepository(db).create_category(category)
        else:
            category_db = await CategoryRepository(db).create_category(category)
            await ProjectCategoryAssociationRepository(db).create_association(
                project_id=project.id,
                category_id=category_db.id,
            )

        return CategoryResponse(
            id=category_db.id,
            name=category_db.name,
        )
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_data: CategoryUpdate, 
    db: AsyncSession = Depends(get_db),
    current_category = Depends(get_current_category)
    ):

    updates = category_data.model_dump(exclude_unset=True)
    return await CategoryRepository(db).update_category(current_category, updates)

@router.delete("/{category_id}")
async def delete_category(
    current_category: Category = Depends(get_current_category),
    db: AsyncSession = Depends(get_db)
    ):

    await CategoryRepository(db).delete_category(current_category)
       