from pydantic import BaseModel
from uuid import UUID
from typing import List

from app.schemas.object import ObjectResponse
from app.schemas.category import CategoryResponse

class AssociationBase(BaseModel):
    object_id: UUID
    category_id: UUID

class AssociationCreate(AssociationBase):
    pass

class AssociationResponse(AssociationBase):
    id: UUID

    class Config:
        from_attributes = True

class AssociationsByObjectResponse(BaseModel):
    object: ObjectResponse
    categories: List[CategoryResponse]

    class Config:
        from_attributes = True

class AssociationsByCategoryResponse(BaseModel):
    category: CategoryResponse
    objects: List[ObjectResponse]

    class Config:
        from_attributes = True
