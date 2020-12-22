from typing import Dict

from app.domain import TypeInfo, MarketGroup
from app.domain.get_market_group_by_type_id import get_market_group_by_type_id


def get_basis_market_group_by_type_id(
        sde_type_ids: Dict[int, TypeInfo],
        sde_market_groups: Dict[int, MarketGroup],
        type_id):
    group_id = get_market_group_by_type_id(sde_type_ids, type_id)
    if group_id is None:
        return None
    __group_id = group_id
    while True:
        if __group_id in [  # 475,  # Manufacture & Research
            # 533,  # Materials (parent:475, см. ниже)
            1035,  # Components (parent:475)
            1872,  # Research Equipment (parent:475)
            955,  # Ship and Module Modifications
            1112,  # Subsystems (parent:955)
        ]:
            return __group_id
        __grp1 = sde_market_groups[__group_id]
        if __grp1.parent_group_id:
            __parent_group_id = __grp1.parent_group_id
            # группа материалов для целей производства должна делиться на подгруппы (производство и заказы
            # в каждой из них решается индивидуально)
            if __parent_group_id in [533,  # Materials
                                     1034,  # Reaction Materials
                                     477,  # Structures (чтобы было понятнее содержимое accounting-отчётов)
                                     ]:
                return __group_id
            __group_id = __parent_group_id
        else:
            return __group_id
    return group_id
