import logging

from typing import List, Optional

from app.schemas.tree import TreeResponse
from app.schemas.product import ProductResponse
from app.db.models import Category, Product
from app.schemas.filter import FilterModel


def map_all_category(category: Category) -> TreeResponse:

    products = [ProductResponse.model_validate(product.product) for product in category.products]

    return TreeResponse(
        id=category.id,
        name=category.name,
        objects=[map_all_category(child) for child in category.children] + products
        )

def apply_filters(products: List[Product], filters: FilterModel) -> List[Product]:
    """
    Применяет фильтры к продуктам.
    """
    def matches(product: Product) -> bool:
        return all([
            filters.name is None or filters.name in product.name,
            filters.description is None or (product.description and filters.description in product.description),
            filters.image is None or (product.image and filters.image in product.image),
            filters.country is None or (product.object and filters.country in product.object.ownership)
        ])

    return [product for product in products if matches(product)]


def map_category(category: Category, filters: Optional[FilterModel] = None) -> Optional[TreeResponse]:
    """
    Рекурсивно строит дерево категорий, исключая пустые категории.
    """
    # Применяем фильтры к продуктам
    products = [assoc.product for assoc in category.products]
    if filters:
        products = apply_filters(products, filters)

    # Преобразуем продукты в ответную схему
    products_response = [ProductResponse.model_validate(product) for product in products]

    # Рекурсивно обрабатываем дочерние категории
    children_response = [map_category(child, filters) for child in category.children]
    # Удаляем пустые дочерние категории
    children_response = [child for child in children_response if child is not None]

    # Если у текущей категории нет ни продуктов, ни дочерних категорий — исключаем её
    if not products_response and not children_response:
        return None

    return TreeResponse(
        id=category.id,
        name=category.name,
        objects=children_response + products_response
    )

def collect_filtered_products(category: Category, filters: Optional[FilterModel] = None) -> List[ProductResponse]:
    """
    Рекурсивно собирает продукты из категории и ее дочерних категорий, применяя фильтры.
    """
    # Получаем продукты из категории
    products = [assoc.product for assoc in category.products]

    # Применяем фильтры
    if filters:
        products = apply_filters(products, filters)

    # Конвертируем продукты в ответную схему
    products_response = [ProductResponse.model_validate(product) for product in products]

    # Рекурсивно обрабатываем дочерние категории
    for child in category.children:
        products_response.extend(collect_filtered_products(child, filters))

    return products_response
