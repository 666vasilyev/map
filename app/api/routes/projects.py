import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Project
from app.repositories.project_repository import ProjectRepository
from app.api.dependencies import get_db, get_current_project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    AllProjectsResponse,
)

router = APIRouter()


@router.get("/", response_model=AllProjectsResponse)
async def get_all_projects(db: AsyncSession = Depends(get_db)):
    """Получить все проекты."""
    projects = await ProjectRepository(db).get_all_projects()
    return AllProjectsResponse(projects=[ProjectResponse.model_validate(project) for project in projects])


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(
    project: Project = Depends(get_current_project), 
    db: AsyncSession = Depends(get_db)):
    """Получить проект по ID."""

    return project

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate, db: AsyncSession = Depends(get_db)
):
    """Создать новый проект."""
    new_project = Project(name=project_data.name, description=project_data.description)
    created_project = await ProjectRepository(db).create_project(new_project)
    return created_project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_data: ProjectUpdate, 
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(get_current_project), 
):
    """Обновить проект."""
    updated_project = await ProjectRepository(db).update_project(
        project, 
        project_data.model_dump(exclude_unset=True), 
    )
    return updated_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project: Project = Depends(get_current_project), 
    db: AsyncSession = Depends(get_db)):
    """Удалить проект."""
    await ProjectRepository(db).delete_project(project)