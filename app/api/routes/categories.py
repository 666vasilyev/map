from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Category
from app.repositories.category_repository import CategoryRepository
from app.repositories.object_repository import ObjectRepository

from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.category_object import AllCategoryResponse, CategoryResponseWithObjects
from app.schemas.object import ObjectResponse

from app.api.dependencies import get_db, get_current_category

router = APIRouter()

@router.get("/", response_model=AllCategoryResponse)
async def list_categories(db: AsyncSession = Depends(get_db)):
    categories = await CategoryRepository(db).get_all_categories()
    if categories:
        
        answers = []

        for category in categories:

            ids = [object.object_id for object in category.objects]
            objects = await ObjectRepository(db).get_object_by_ids(ids)

            category_to_return = CategoryResponseWithObjects(
                id=category.id,
                name=category.name,
                objects=[ObjectResponse.model_validate(object) for object in objects]
            )

            answers.append(category_to_return)

        return AllCategoryResponse(categories=answers)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categories not found")

@router.get("/{category_id}", response_model=CategoryResponseWithObjects)
async def get_category_by_id(
    db: AsyncSession = Depends(get_db),
    current_category: Category = Depends(get_current_category)
    ):

    ids = [object.object_id for object in current_category.objects]
    objects = await ObjectRepository(db).get_object_by_ids(ids)

    category_to_return = CategoryResponseWithObjects(
        id=current_category.id,
        name=current_category.name,
        objects=[ObjectResponse.model_validate(object) for object in objects]
    )


    return category_to_return

@router.post("/", response_model=CategoryResponse)
async def create_category(category_data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = Category(name=category_data.name)
    return await CategoryRepository(db).create_category(category)

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
    current_category = Depends(get_current_category),
    db: AsyncSession = Depends(get_db)
    ):
    await CategoryRepository(db).delete_category(current_category)
       