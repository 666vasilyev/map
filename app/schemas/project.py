from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List

from app.schemas.category import CategoryResponse


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    category_ids: Optional[List[UUID]] = None


class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: UUID

    class Config:
        from_attributes = True


class AllProjectsResponse(BaseModel):
    projects: List[ProjectResponse]
