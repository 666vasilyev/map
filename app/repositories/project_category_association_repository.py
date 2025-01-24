import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from typing import List

from app.db.models import ProjectCategoryAssociation


class ProjectCategoryAssociationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_association_by_id(self, association_id: uuid.UUID) -> ProjectCategoryAssociation:
        """Получить ассоциацию по ID."""
        result = await self.db.execute(
            select(ProjectCategoryAssociation).where(ProjectCategoryAssociation.id == association_id)
        )
        association = result.scalar_one_or_none()
        if not association:
            raise NoResultFound(f"Association with id {association_id} not found")
        return association

    async def get_associations_by_project(self, project_id: uuid.UUID) -> List[ProjectCategoryAssociation]:
        """Получить все ассоциации для заданного проекта."""
        result = await self.db.execute(
            select(ProjectCategoryAssociation)
            .options(
                joinedload(ProjectCategoryAssociation.project),
                joinedload(ProjectCategoryAssociation.category)
            )
            .where(ProjectCategoryAssociation.project_id == project_id)
        )
        return result.scalars().all()

    async def get_associations_by_category(self, category_id: uuid.UUID) -> List[ProjectCategoryAssociation]:
        """Получить все ассоциации для заданной категории."""
        result = await self.db.execute(
            select(ProjectCategoryAssociation)
            .options(
                joinedload(ProjectCategoryAssociation.project),
                joinedload(ProjectCategoryAssociation.category)
            )
            .where(ProjectCategoryAssociation.category_id == category_id)
        )
        return result.scalars().all()

    async def create_association(self, project_id: uuid.UUID, category_id: uuid.UUID) -> ProjectCategoryAssociation:
        """Создать новую ассоциацию между проектом и категорией."""
        association = ProjectCategoryAssociation(project_id=project_id, category_id=category_id)
        self.db.add(association)
        await self.db.commit()
        await self.db.refresh(association)
        return association

    async def create_associations(
        self, project_id: uuid.UUID, category_ids: List[uuid.UUID]
    ) -> List[ProjectCategoryAssociation]:
        
        """Создать несколько ассоциаций для проекта."""
        associations = [
            ProjectCategoryAssociation(project_id=project_id, category_id=category_id)
            for category_id in category_ids
        ]
        self.db.add_all(associations)
        await self.db.commit()
        return associations

    async def delete_associations_by_project(self, project_id: uuid.UUID) -> None:
        """Удалить все ассоциации, связанные с проектом."""
        associations = await self.get_associations_by_project(project_id)
        for association in associations:
            await self.db.delete(association)
        await self.db.commit()

    async def delete_association(self, association: ProjectCategoryAssociation) -> None:
        """Удалить одну ассоциацию."""
        await self.db.delete(association)
        await self.db.commit()
