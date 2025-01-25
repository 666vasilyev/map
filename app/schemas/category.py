from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    parent_id: Optional[UUID] = None  # Добавляем поле для родительской категории
    project_id: UUID

class CategoryCreateV2(CategoryBase):
    id: Optional[UUID] = None

class CategoryResponse(CategoryBase):
    id: UUID

    class Config:
        from_attributes = True

class AllCategoryResponse(BaseModel):
    categories: List[CategoryResponse]

    class Config:
        exclude_none = True


class CategoryUpdate(BaseModel):
    name: Optional[str] = None

