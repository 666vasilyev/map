from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List, Optional

from app.db.models import Project, ProjectCategoryAssociation
from app.repositories.project_category_association_repository import ProjectCategoryAssociationRepository

class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.association_repo = ProjectCategoryAssociationRepository(db)

    async def get_all_projects(self) -> List[Project]:
        """Получить все проекты."""
        result = await self.db.execute(
            select(Project).options(joinedload(Project.categories))
        )
        return result.unique().scalars().all()

    async def get_project_by_id(self, project_id: UUID) -> Optional[Project]:
        """Получить проект по ID."""
        result = await self.db.execute(
            select(Project)
            .options(joinedload(Project.categories)
                     .joinedload(ProjectCategoryAssociation.category))
            .where(Project.id == project_id)
        )
        return result.unique().scalar_one_or_none()

    async def create_project(self, project: Project, category_ids: List[UUID]) -> Project:
        """Создать проект и ассоциации."""
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)

        if category_ids:
            await self.association_repo.create_associations(project.id, category_ids)

        return project

    async def delete_project(self, project: Project) -> None:
        """Удалить проект и связанные с ним ассоциации."""
        await self.association_repo.delete_associations_by_project(project.id)
        await self.db.delete(project)
        await self.db.commit()

    async def update_project(
        self, project: Project, updates: dict, category_ids: List[UUID]
    ) -> Project:
        """Обновить проект и его ассоциации."""
        for key, value in updates.items():
            setattr(project, key, value)
        await self.db.commit()
        await self.db.refresh(project)

        # Обновляем ассоциации
        await self.association_repo.delete_associations_by_project(project.id)
        if category_ids:
            await self.association_repo.create_associations(project.id, category_ids)

        return project
