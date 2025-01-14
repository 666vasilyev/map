import uuid
from typing import List, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class ObjectCategoryAssociation(Base):
    __tablename__ = "object_category_association"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    object_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("objects.id"))
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"))

    object: Mapped["Object"] = relationship(
        "Object", 
        back_populates="object_category_associations"
    )
    
    category: Mapped["Category"] = relationship(
        "Category", 
        back_populates="object_category_associations"
    )


class Chain(Base):
    __tablename__ = "chains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    source_object_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("objects.id"))
    target_object_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("objects.id"))

    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("products.id"), nullable=True)

    source_object: Mapped["Object"] = relationship(
        "Object", back_populates="chains_source", foreign_keys=[source_object_id]
    )

    # target_object: Mapped["Object"] = relationship(
    #     "Object", back_populates="chains_target", foreign_keys=[target_object_id]
    # )

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
    category: Mapped[str] = mapped_column(nullable=False)
    area: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[int] = mapped_column(nullable=False)
    links: Mapped[Optional[str]] = mapped_column(nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(nullable=True)
    image: Mapped[Optional[str]] = mapped_column(nullable=True)
    file_storage: Mapped[Optional[str]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    # Продукты, производимые объектом
    products: Mapped[List["Product"]] = relationship(
        "Product", back_populates="object"
    )

    # Цепочки, где объект источник
    chains_source: Mapped[List["Chain"]] = relationship(
        "Chain", 
        back_populates="source_object", 
        foreign_keys="[Chain.source_object_id]"
    )

    # Цепочки, где объект цель
    # chains_target: Mapped[List["Chain"]] = relationship(
    #     "Chain", 
    #     back_populates="target_object", 
    #     foreign_keys="[Chain.target_object_id]"
    # )

    object_category_associations: Mapped[List["ObjectCategoryAssociation"]] = relationship(
        "ObjectCategoryAssociation", 
        back_populates="object"
    )

class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    image: Mapped[Optional[str]] = mapped_column(nullable=True)
    object_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("objects.id"), nullable=True)

    # Связь с объектом
    object: Mapped["Object"] = relationship(
        "Object", 
        back_populates="products"
        )

    # Связь с цепочками
    chains: Mapped[List["Chain"]] = relationship(
        "Chain", 
        back_populates="product"
    )

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    
    object_category_associations: Mapped[List["ObjectCategoryAssociation"]] = relationship(
        "ObjectCategoryAssociation", 
        back_populates="category", 
    )