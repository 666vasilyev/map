from pydantic import BaseModel
from uuid import UUID
from typing import List

class ChainBase(BaseModel):
    source_object_id: UUID
    target_object_id: UUID
    product_id: UUID

class ChainCreate(ChainBase):
    pass

class ChainResponse(ChainBase):
    id: UUID

    class Config:
        from_attributes = True

class AllChainResponse(BaseModel):
    chains: List[ChainResponse]

class ChainUpdate(BaseModel):
    source_object_id: UUID | None
    target_object_id: UUID | None

class ChainsByProductResponse(BaseModel):
    product_id: UUID
    chains: List[ChainResponse]

    class Config:
        from_attributes = True