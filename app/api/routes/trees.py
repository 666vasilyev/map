import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Category, Project
from app.repositories.category_repository import CategoryRepository

from app.schemas.tree import (
    TreeResponse, 
    AllTreeResponse,
)

from app.schemas.filter import FilterModel
from app.api.dependencies import get_db, get_current_category, get_current_project
from app.api.routes.utils import map_category, map_all_category

router = APIRouter()
logging.basicConfig(level=logging.INFO)

@router.get("/all", response_model=AllTreeResponse)
async def get_tree(db: AsyncSession = Depends(get_db)):

    categories = await CategoryRepository(db).get_root_categories_with_relationships()

    if not categories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categories not found")

    answers = []
    for category in categories:
        category_to_return = map_all_category(category)
        answers.append(category_to_return)

    return AllTreeResponse(categories=answers)


@router.get("/{category_id}", response_model=TreeResponse)
async def get_tree_by_id(
    category: Category = Depends(get_current_category),
    db: AsyncSession = Depends(get_db)
    ):

    category_to_return = map_category(category)

    return category_to_return

@router.get("/project/{project_id}", response_model=AllTreeResponse)
async def get_tree_by_project(
    project: Project = Depends(get_current_project),
    db: AsyncSession = Depends(get_db)
    ):

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    category_ids = [association.category_id for association in project.categories]

    categories = await CategoryRepository(db).get_category_by_ids(category_ids)

    # Построение дерева категорий
    tree = [map_category(category) for category in categories]

    return AllTreeResponse(categories=tree)


@router.post("/project/{project_id}/filtered", response_model=AllTreeResponse)
async def get_tree_by_project_with_filters(
    filters: FilterModel,
    project: Project = Depends(get_current_project),
    db: AsyncSession = Depends(get_db)
):

    # Получаем категории проекта
    category_ids = [association.category_id for association in project.categories]
    categories = await CategoryRepository(db).get_category_by_ids(category_ids)

    # Строим дерево с применением фильтров
    filtered_tree = [
        map_category(category, filters) for category in categories
    ]
    filtered_tree = [category for category in filtered_tree if category is not None]  # Убираем None


    # Возвращаем дерево
    return AllTreeResponse(categories=filtered_tree)
