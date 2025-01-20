from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional

from app.schemas.category import CategoryBase, CategoryResponse
from app.schemas.object import ObjectBase, ObjectResponse



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

