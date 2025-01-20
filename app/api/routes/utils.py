from typing import List

from app.schemas.category_object import CategoryResponseWithObjects
from app.schemas.object import ObjectResponse
from app.db.models import Category, Object

def map_category_with_objects(category: Category, objects: List[Object]) -> CategoryResponseWithObjects:
    ids = {obj.id for obj in objects}
    return CategoryResponseWithObjects(
        id=category.id,
        name=category.name,
        objects=[ObjectResponse.model_validate(obj) for obj in objects if obj.id in ids],
        children=[map_category_with_objects(child, objects) for child in category.children]
    )
