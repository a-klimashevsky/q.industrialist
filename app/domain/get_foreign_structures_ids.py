from typing import List

from app.domain import Asset


def get_foreign_structures_ids(corp_assets_data: List[Asset]):
    foreign_structs_ids = []
    for a in corp_assets_data:
        # проверяем либо location_flag=OfficeFolder, либо type_id=27 (Office)
        if a.type_id == 27:
            # если будет найден Офис корпорации, то надо найти станцию
            # в том случае, если её нет в ассетах, то станция принадлежит другой
            # корпорации (пропускаем NPC-станции, с int32-кодами, и формируем
            # список из станций с int64-кодами)
            station_id = a.location_id
            if station_id < 1000000000000:
                continue
            found = False
            for _a in corp_assets_data:
                if _a.item_id == station_id:
                    found = True
                    break
            if not found:
                if 0 == foreign_structs_ids.count(station_id):
                    foreign_structs_ids.append(station_id)
        elif (a.location_flag == "CorpDeliveries") and (a.location_type == "item"):
            # если будут найдены корпоративные delivery, то следует иметь в виду, что
            # всякое corp-delivery всегда находится в разделе "входящие" на станциях, так
            # что всякая локация corp-deliveries - это станции
            location_id = a.location_id
            if location_id < 1000000000000:
                continue
            if 0 == foreign_structs_ids.count(location_id):
                foreign_structs_ids.append(location_id)
    return foreign_structs_ids
