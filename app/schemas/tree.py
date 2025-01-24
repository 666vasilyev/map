from uuid import UUID
from pydantic import BaseModel
from typing import List

from app.schemas.category import CategoryBase

class TreeResponse(CategoryBase):
    id: UUID
    objects: List  # Список объектов в категории

    class Config:
        from_attributes = True

class AllTreeResponse(BaseModel):
    categories: List[TreeResponse]

    class Config:
        exclude_none = True

