from uuid import UUID
from pydantic import BaseModel
from typing import List

class CategoryBase(BaseModel):
    name: str

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