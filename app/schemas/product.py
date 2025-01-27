from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    country: Optional[str] = None

class ProductCreate(ProductBase):
    categories: List[UUID]
    pass

class ProductResponse(ProductBase):
    id: UUID

    class Config:
        from_attributes = True

class AllProductResponse(BaseModel):
    products: List[ProductResponse]

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    country: Optional[str] = None

class ProductIds(BaseModel):
    ids: List[UUID]

