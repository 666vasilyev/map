import uuid
from typing import List, Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

class Base(DeclarativeBase):
    pass

class ProductCategoryAssociation(Base):
    __tablename__ = "product_category_association"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"))

    product: Mapped["Product"] = relationship(
        "Product", 
        back_populates="categories",
        lazy="joined"
    )
    
    category: Mapped["Category"] = relationship(
        "Category", 
        back_populates="products",
        lazy="joined"
    )

class ProjectCategoryAssociation(Base):
    __tablename__ = "project_category_association"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)

    # Связь с Project
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="categories", 
        lazy="joined"
    )

    # Связь с Category
    category: Mapped["Category"] = relationship(
        "Category", 
        back_populates="projects", 
        lazy="joined"
    )


class Chain(Base):
    __tablename__ = "chains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    source_object_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("objects.id"))
    target_object_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("objects.id"))

    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("products.id"))

    source_object: Mapped["Object"] = relationship(
        "Object", back_populates="chains_source", foreign_keys=[source_object_id]
    )

    target_object: Mapped["Object"] = relationship(
        "Object", back_populates="chains_target", foreign_keys=[target_object_id], lazy='joined'
    )

    product: Mapped["Product"] = relationship(
        "Product", back_populates="chains", foreign_keys=[product_id]
    )

class Object(Base):
    __tablename__ = "objects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    x: Mapped[float] = mapped_column(nullable=False)
    y: Mapped[float] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    ownership: Mapped[Optional[str]] = mapped_column(nullable=True)
    area: Mapped[float] = mapped_column(nullable=False)
    object_status: Mapped[int] = mapped_column(nullable=False)
    links: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True) 
    icon: Mapped[Optional[str]] = mapped_column(nullable=True)
    image: Mapped[Optional[str]] = mapped_column(nullable=True)
    file_storage: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("projects.id"), nullable=True)

    # Продукты, производимые объектом
    products: Mapped[List["Product"]] = relationship(
        "Product", back_populates="object"
    )

    # Цепочки, где объект источник
    chains_source: Mapped[List["Chain"]] = relationship(
        "Chain", 
        back_populates="source_object", 
        foreign_keys="[Chain.source_object_id]",
        lazy='joined',
        cascade="all, delete-orphan"

    )

    # Цепочки, где объект потребитель
    chains_target: Mapped[List["Chain"]] = relationship(
        "Chain", 
        back_populates="target_object", 
        foreign_keys="[Chain.target_object_id]",
        lazy='joined',
        cascade="all, delete-orphan"
    )

    # Самореферентное отношение для филиалов (дочерних объектов)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("objects.id"), 
        nullable=True
    )

    parent: Mapped[Optional["Object"]] = relationship(
        "Object", 
        remote_side=[id], 
        back_populates="branches"
    )

    branches: Mapped[Optional[List["Object"]]] = relationship(
        "Object", 
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="objects",
        lazy="joined"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    image: Mapped[Optional[str]] = mapped_column(nullable=True)

    country: Mapped[str] = mapped_column(nullable=True, default=None)
    
    object_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("objects.id"), nullable=True)

    # Связь с объектом
    object: Mapped["Object"] = relationship(
        "Object", 
        back_populates="products"
        )

    # Связь с цепочками
    chains: Mapped[List["Chain"]] = relationship(
        "Chain", 
        back_populates="product",
        cascade="all, delete-orphan"  # Указание каскадного удаления
    )

    categories: Mapped[List["ProductCategoryAssociation"]] = relationship(
        "ProductCategoryAssociation", 
        back_populates="product",
        cascade="all, delete-orphan"  # Указание каскадного удаления
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)

    # Самореферентное отношение для родителя
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)

    parent: Mapped[Optional["Category"]] = relationship(
        "Category", 
        remote_side=[id], 
        back_populates="children" 
    )

    # Самореферентное отношение для дочерних категорий
    children: Mapped[List["Category"]] = relationship(
        "Category", 
        back_populates="parent", 
        lazy="joined"
    )

    # Отношение с ProductCategoryAssociation
    products: Mapped[List["ProductCategoryAssociation"]] = relationship(
        "ProductCategoryAssociation", 
        back_populates="category", 
        lazy="joined",
        cascade="all, delete-orphan"  # Указание каскадного удаления
    )

    projects: Mapped[List["ProjectCategoryAssociation"]] = relationship(
        "ProjectCategoryAssociation",
        back_populates="category",
        lazy="joined",
        cascade="all, delete-orphan"  # Указание каскадного удаления
    )


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    categories: Mapped[List["ProjectCategoryAssociation"]] = relationship(
        "ProjectCategoryAssociation",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    objects: Mapped[List["Object"]] = relationship(
        "Object",
        back_populates="project",
        lazy="joined"
    )


