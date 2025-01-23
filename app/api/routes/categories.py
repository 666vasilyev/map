import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.models import Category
from app.repositories.category_repository import CategoryRepository
from app.repositories.object_repository import ObjectRepository
from app.repositories.association_repository import AssociationRepository

from app.schemas.category import (CategoryCreate, 
                                  CategoryTreeResponse, 
                                  CategoryUpdate, 
                                  AllCategoryResponse,
                                  CategoryResponse
                                  )
from app.schemas.object import ObjectSmallResponse

from app.api.dependencies import get_db, get_current_category
from app.api.routes.utils import map_category

router = APIRouter()
logging.basicConfig(level=logging.INFO)

@router.get("/tree", response_model=AllCategoryResponse)
async def get_category_tree(db: AsyncSession = Depends(get_db)):

    categories = await CategoryRepository(db).get_root_categories_with_relationships()

    if not categories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categories not found")

    answers = []
    for category in categories:
        # logging.info([child for child in category.children])
        category_to_return = map_category(category)
        answers.append(category_to_return)

    # cleaned_answers = [answer for answer in answers if answer.parent_id is None]
    return AllCategoryResponse(categories=answers)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(
    db: AsyncSession = Depends(get_db),
    current_category: Category = Depends(get_current_category)
    ):

    return current_category

@router.post("/", response_model=CategoryResponse)
async def create_category(category_data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = Category(
        name=category_data.name
        )

    # Устанавливаем родительскую категорию, если передан parent_id
    if category_data.parent_id:
        parent_category = await CategoryRepository(db).get_category_by_id(category_data.parent_id)
        if not parent_category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent category not found")
        category.parent = parent_category
        
    try:
        return await CategoryRepository(db).create_category(category)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    except Exception as e:
        logging.error(f"An error occurred while creating a category: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while creating a category: {e}")

@router.put("/{category_id}", response_model=CategoryTreeResponse)
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
    for object in current_category.objects:
        await AssociationRepository(db).delete_association(object.id)

    await CategoryRepository(db).delete_category(current_category)
       