from typing import Dict

from app.domain import TypeInfo


def get_market_group_by_type_id(sde_type_ids: Dict[int, TypeInfo], type_id: int):
    if not (type_id in sde_type_ids):
        return None
    type_dict = sde_type_ids[type_id]
    return type_dict.market_group_id
