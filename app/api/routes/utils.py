import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.category import CategoryTreeResponse
from app.schemas.object import ObjectSmallResponse
from app.db.models import Category

from app.repositories.category_repository import CategoryRepository

def map_category(category: Category) -> CategoryTreeResponse :
    objects = [ObjectSmallResponse.model_validate(object.object) for object in category.objects]

    return CategoryTreeResponse(
        id=category.id,
        name=category.name,
        objects=[map_category(child) for child in category.children] + objects
        )

