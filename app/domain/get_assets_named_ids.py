from typing import List

from app.domain import Asset


def get_assets_named_ids(corp_assets_data: List[Asset]):
    ass_cont_ids = []
    for a in corp_assets_data:
        if not a.is_singleton:
            continue  # пропускаем экземпляры контейнеров, сложенные в стопки (у них нет уник. id и названий тоже не будет)
        loc_flag = a.location_flag
        if not (loc_flag[:-1] == "CorpSAG") and not (loc_flag == "Unlocked") and not (loc_flag == "AutoFit"):
            continue  # пропускаем дронов в дронбеях, патроны в карго, корабли в ангарах и т.п.
        if a.type_id in [17363,   # Small Audit Log Secure Container
                            17364,   # Medium Audit Log Secure Container
                            17365,   # Large Audit Log Secure Container
                            17366,   # Station Container
                            17367,   # Station Vault Container
                            17368,   # Station Warehouse Container
                            2233,    # Customs Office
                            24445,   # Giant Freight Container
                            33003,   # Enormous Freight Container
                            33005,   # Huge Freight Container
                            33007,   # Large Freight Container
                            33009,   # Medium Freight Container
                            33011,   # Small Freight Container
                            35825,   # Raitaru
                            35826,   # Azbel
                            35827,   # Sotiyo
                            35828,   # Medium Laboratory
                            35829,   # Large Laboratory
                            35830,   # X-Large Laboratory
                            35832,   # Astrahus
                            35833,   # Fortizar
                            35834,   # Keepstar
                            35835,   # Athanor
                            35836    # Tatara
                           ]:
            if ass_cont_ids.count(a.item_id) == 0:
                ass_cont_ids.append(a.item_id)
    return ass_cont_ids
