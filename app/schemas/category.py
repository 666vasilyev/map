from uuid import UUID
from pydantic import BaseModel
from typing import List

from app.schemas.object import ObjectResponse

class CategoryBase(BaseModel):
    name: str
    objects: List[ObjectResponse]

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: UUID

    class Config:
        from_attributes = True

class AllCategoryResponse(BaseModel):
    categories: List[CategoryResponse]

class CategoryUpdate(BaseModel):
    name: str | None