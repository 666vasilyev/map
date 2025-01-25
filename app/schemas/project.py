from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: UUID

    class Config:
        from_attributes = True


class AllProjectsResponse(BaseModel):
    projects: List[ProjectResponse]
