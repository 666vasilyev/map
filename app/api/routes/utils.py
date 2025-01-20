from typing import List

from app.schemas.category import CategoryTreeResponse
from app.schemas.object import ObjectSmallResponse
from app.db.models import Category, Object

def map_category(category: Category, objects: List[Object]) -> CategoryTreeResponse :
    ids = {obj.object_id for obj in category.objects}
    mapped_objects = [ObjectSmallResponse.model_validate(obj) for obj in objects if obj.id in ids]
    return CategoryTreeResponse(
        id=category.id,
        name=category.name,
        parent_id=category.parent_id,
        objects=[map_category(child, objects) for child in category.children] + mapped_objects
        )

