from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List

from app.schemas.object import ObjectSmallResponse

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    parent_id: Optional[UUID] = None  # Добавляем поле для родительской категории


class CategoryResponse(CategoryBase):
    id: UUID

    class Config:
        from_attributes = True


class CategoryTreeResponse(CategoryBase):
    id: UUID
    objects: List  # Список объектов в категории

    class Config:
        from_attributes = True

class AllCategoryResponse(BaseModel):
    categories: List[CategoryTreeResponse]

    class Config:
        exclude_none = True


class CategoryUpdate(BaseModel):
    name: str | None

class CategoryResponseWithObjects(CategoryBase):
    id: UUID
    objects: List[ObjectSmallResponse]

    class Config:
        from_attributes = True