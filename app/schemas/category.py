from uuid import UUID
from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    parent_id: Optional[UUID] = None  # Добавляем поле для родительской категории


class CategoryResponse(CategoryBase):
    id: UUID
    parent: Optional["CategoryResponse"] = None  # Ссылка на родительскую категорию

    class Config:
        from_attributes = True

class CategoryUpdate(BaseModel):
    name: str | None

CategoryResponse.model_rebuild()