from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class ProductBase(BaseModel):
    name: str
    description: str | None
    image: str | None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: UUID
    object_id: Optional[UUID]

    class Config:
        from_attributes = True

class AllProductResponse(BaseModel):
    products: List[ProductResponse]

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    image: Optional[str]
    object_id: Optional[UUID]