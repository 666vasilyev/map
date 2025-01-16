from uuid import UUID
from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: UUID

    class Config:
        from_attributes = True

class CategoryUpdate(BaseModel):
    name: str | None