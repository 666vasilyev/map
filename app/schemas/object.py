from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

from app.schemas.enums import StatusEnum

class ObjectBase(BaseModel):
    x: float
    y: float
    name: str
    ownership: Optional[str]
    area: float
    status: StatusEnum
    links: Optional[str]
    icon: Optional[str]
    image: Optional[str]
    file_storage: Optional[str]
    description: Optional[str]

class ObjectCreate(ObjectBase):
    pass


class ObjectSmallResponse(BaseModel):
    x: float
    y: float
    id: UUID
    name: str
    icon: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True

class ObjectResponse(ObjectBase):
    id: UUID

    class Config:
        from_attributes = True


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

class AllObjectsResponse(BaseModel):
    objects: List[ObjectResponse]


class ObjectCoordinates(BaseModel):
    x: float
    y: float
    id: UUID


class ObjectChainResponse(ObjectSmallResponse):
    chains: Optional[List[ObjectCoordinates]] = None

class AllObjectChainResponse(BaseModel):
    objects: List[ObjectChainResponse]

