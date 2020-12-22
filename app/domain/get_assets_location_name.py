from typing import Dict, List

from app.domain import InventoryLocation, AssetName
from app.esi import StructureData

#TODO (a.klimashevsky): I dont kwow why I change it
def get_assets_location_name(
        location_id: str,
        sde_inv_names: Dict[int, str],
        sde_inv_items: Dict[int, InventoryLocation],
        corp_ass_names_data: List[AssetName],
        foreign_structures_data: Dict[str, StructureData]):
    region_id = None
    region_name = None
    loc_name = None
    foreign = False
    loc_is_not_virtual = __represents_int(location_id)
    if loc_is_not_virtual and (int(location_id) < 1000000000000):
        if location_id in sde_inv_names:
            loc_name = sde_inv_names[location_id]
            if location_id in sde_inv_items:
                root_item = sde_inv_items[location_id]
                if root_item.type_id == 5:  # Solar System
                    # constellation_name = sde_inv_names[str(root_item["locationID"])]
                    constellation_item = sde_inv_items[root_item.parent_location_id]  # Constellation
                    region_id = constellation_item.parent_location_id
                    region_name = sde_inv_names[region_id]
    else:
        if not loc_is_not_virtual and (location_id[:-1])[-7:] == "CorpSAG":
            loc_name = 'Corp Security Access Group {}'.format(location_id[-1:])
        else:
            loc_name = next((n.name for n in corp_ass_names_data if n.item_id == location_id), None)
            if loc_name is None:
                loc_name = next(
                    (foreign_structures_data[fs].name for fs in foreign_structures_data if int(fs) == location_id),
                    None)
                foreign = False if loc_name is None else True
    return region_id, region_name, loc_name, foreign


def __represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False
