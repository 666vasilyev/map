from pydantic import BaseModel, HttpUrl
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
    links: Optional[List[str]] = None # для корректной работы со старыми данными
    icon: Optional[str]
    image: Optional[str]
    file_storage: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class ObjectCreate(ObjectBase):
    links: Optional[List[HttpUrl]] = None



class ObjectSmallResponse(BaseModel):
    x: float
    y: float
    id: UUID
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None

    class Config:
        from_attributes = True

class ObjectResponse(ObjectBase):
    id: UUID
    parent_id: Optional[UUID] = None
    branches: Optional[List["ObjectSmallResponse"]] = None


    class Config:
        from_attributes = True


class ObjectUpdate(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    name: Optional[str] = None
    ownership: Optional[str] = None
    category: Optional[str] = None
    area: Optional[float] = None
    status: Optional[StatusEnum] = None
    links: Optional[List[HttpUrl]] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    file_storage: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None

class AllObjectsResponse(BaseModel):
    objects: List[ObjectResponse]

class LocationCheckRequest(BaseModel):
    x: float
    y: float


class ObjectCoordinates(LocationCheckRequest):
    id: UUID


class ObjectChainResponse(ObjectSmallResponse):
    chains: Optional[List[ObjectCoordinates]] = None

class AllObjectChainResponse(BaseModel):
    objects: List[ObjectChainResponse]

class AllSmallObjectsResponse(BaseModel):
    objects: List[ObjectSmallResponse]