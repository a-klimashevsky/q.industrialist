from typing import Dict

from app.domain import TypeInfo


def get_item_name_by_type_id(type_ids: Dict[int, TypeInfo], type_id:int):
    if not type_id in type_ids:
        return str(type_id)

    type_dict = type_ids[type_id]
    return type_dict.name.get("en", str(type_id))
