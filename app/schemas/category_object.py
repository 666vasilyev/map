from uuid import UUID
from pydantic import BaseModel
from typing import List

from app.schemas.category import CategoryBase, CategoryResponse
from app.schemas.object import ObjectBase, ObjectResponse

class CategoryResponseWithObjects(CategoryBase):
    id: UUID
    objects: List[ObjectResponse]
    children: List["CategoryResponseWithObjects"]  # Список дочерних категорий

    class Config:
        from_attributes = True

class AllCategoryResponse(BaseModel):
    categories: List[CategoryResponseWithObjects]


class ObjectResponseWithCategories(ObjectBase):
    id: UUID
    categories: List[CategoryResponse]

    class Config:
        from_attributes = True

class AllObjectsResponse(BaseModel):
    objects: List[ObjectResponseWithCategories]

class ObjectCreate(ObjectBase):
    categories: list[UUID]
    pass

CategoryResponseWithObjects.model_rebuild()
