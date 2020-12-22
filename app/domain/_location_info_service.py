from abc import ABC, abstractmethod

from app.domain import LocationInfo
from app.gateways import GetInventoryLocationNamesGateway, InventoryLocationGateway, GetCorpAssetsNamesGateway, \
    CorpAssetsGateway, ForeignStructuresGateway


class LocationInfoService(ABC):
    @abstractmethod
    def get_into(self, item_id) -> LocationInfo:
        pass


class LocationInfoServiceImpl(LocationInfoService):
    _inventory_names_gateway: GetInventoryLocationNamesGateway
    _inventory_location_gateway: InventoryLocationGateway
    _corp_assets_names_gateway: GetCorpAssetsNamesGateway
    _corp_assets_gateway: CorpAssetsGateway
    _foreign_structures_gateway: ForeignStructuresGateway

    def __init__(self,
                 inventory_names_gateway: GetInventoryLocationNamesGateway,
                 inventory_location_gateway: InventoryLocationGateway,
                 corp_assets_names_gateway: GetCorpAssetsNamesGateway,
                 corp_assets_gateway: CorpAssetsGateway,
                 foreign_structures_gateway: ForeignStructuresGateway,
                 ):
        self._inventory_names_gateway = inventory_names_gateway
        self._inventory_location_gateway = inventory_location_gateway
        self._corp_assets_names_gateway = corp_assets_names_gateway
        self._corp_assets_gateway = corp_assets_gateway
        self._foreign_structures_gateway = foreign_structures_gateway
        pass

    def get_into(self, item_id) -> LocationInfo:

        sde_inv_names = self._inventory_names_gateway.names()
        sde_inv_items = self._inventory_location_gateway.get_inventory_locations()
        corp_assets_data = self._corp_assets_gateway.assets()
        corp_ass_names_data = self._corp_assets_names_gateway.asets_name(corp_assets_data)
        foreign_structures_data = self._foreign_structures_gateway.structures(corp_assets_data)

        region_id = None
        region_name = None
        loc_name = None
        foreign = False
        loc_is_not_virtual = self.__represents_int(item_id)
        if loc_is_not_virtual and (int(item_id) < 1000000000000):
            if item_id in sde_inv_names:
                loc_name = sde_inv_names[item_id]
                if item_id in sde_inv_items:
                    root_item = sde_inv_items[item_id]
                    if root_item.type_id == 5:  # Solar System
                        # constellation_name = sde_inv_names[str(root_item["locationID"])]
                        constellation_item = sde_inv_items[root_item.parent_location_id]  # Constellation
                        region_id = constellation_item.parent_location_id
                        region_name = sde_inv_names[region_id]
        else:
            if not loc_is_not_virtual and (item_id[:-1])[-7:] == "CorpSAG":
                loc_name = 'Corp Security Access Group {}'.format(item_id[-1:])
            else:
                loc_name = next((n.name for n in corp_ass_names_data if n.item_id == item_id), None)
                if loc_name is None:
                    loc_name = next(
                        (foreign_structures_data[fs].name for fs in foreign_structures_data if int(fs) == item_id),
                        None)
                    foreign = False if loc_name is None else True
        return LocationInfo(
            region_id=region_id,
            region_name=region_name,
            name=loc_name,
            foreign=foreign
        )

    @staticmethod
    def __represents_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False
        except TypeError:
            return False
