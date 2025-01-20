from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.models import Category
from app.repositories.category_repository import CategoryRepository
from app.repositories.object_repository import ObjectRepository
from app.repositories.association_repository import AssociationRepository


from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.category_object import AllCategoryResponse, CategoryResponseWithObjects
from app.schemas.object import ObjectResponse

from app.api.dependencies import get_db, get_current_category

from app.api.routes.utils import map_category_with_objects

router = APIRouter()

@router.get("/", response_model=AllCategoryResponse)
async def list_categories(db: AsyncSession = Depends(get_db)):
    categories = await CategoryRepository(db).get_all_categories_with_children()
    if not categories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categories not found")

    answers = []
    for category in categories:
        # Gather all object IDs from the category's associations
        ids_list = [object.object_id for object in category.objects]
        ids = set(ids_list)

        # Fetch all objects associated with the IDs
        objects = await ObjectRepository(db).get_object_by_ids(ids)

        # Map categories and their objects using the utility function
        category_to_return = map_category_with_objects(category, objects)
        answers.append(category_to_return)

    return AllCategoryResponse(categories=answers)


@router.get("/{category_id}", response_model=CategoryResponseWithObjects)
async def get_category_by_id(
    db: AsyncSession = Depends(get_db),
    current_category: Category = Depends(get_current_category)
    ):

    ids = [object.object_id for object in current_category.objects]
    objects = await ObjectRepository(db).get_object_by_ids(ids)

    category_to_return = map_category_with_objects(current_category, objects)
    
    return category_to_return

@router.post("/", response_model=CategoryResponse)
async def create_category(category_data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = Category(name=category_data.name)

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
    for object in current_category.objects:
        await AssociationRepository(db).delete_association(object.id)

    await CategoryRepository(db).delete_category(current_category)
       