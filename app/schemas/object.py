from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from app.schemas.enums import StatusEnum

class ObjectBase(BaseModel):
    x: float
    y: float
    name: str
    ownership: Optional[str]
    category: str
    area: float
    status: StatusEnum
    links: Optional[str]
    icon: Optional[str]
    image: Optional[str]
    file_storage: Optional[str]
    description: Optional[str]

class ObjectCreate(ObjectBase):
    pass

class ObjectResponse(ObjectBase):
    id: UUID

    class Config:
        from_attributes = True

class AllObjectsResponse(BaseModel):
    objects: List[ObjectResponse]

class ObjectUpdate(BaseModel):
    x: Optional[float]
    y: Optional[float]
    name: Optional[str]
    ownership: Optional[str]
    category: Optional[str]
    area: Optional[float]
    status: Optional[StatusEnum]
    links: Optional[str]
    icon: Optional[str]
    image: Optional[str]
    file_storage: Optional[str]
    description: Optional[str]