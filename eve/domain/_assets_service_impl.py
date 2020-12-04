from typing import Dict

from eve.domain import AssetsService, AssetsTree, AssetTreeItem, get_assets_tree
from eve.gateways import CorpAssetsGateway, ForeignStructuresGateway, InventoryLocationGateway


class AssetsServiceImpl(AssetsService):
    _corp_assets_gateway: CorpAssetsGateway
    _foreign_structures_gateway: ForeignStructuresGateway
    _inventory_locations_gateway: InventoryLocationGateway
    _corporation_name: str

    def __init__(self,
                 corporation_name: str,
                 corp_assets_gateway: CorpAssetsGateway,
                 foreign_structures_gateway: ForeignStructuresGateway,
                 inventory_locations_gateway: InventoryLocationGateway,
                 ):
        self._corporation_name = corporation_name
        self._corp_assets_gateway = corp_assets_gateway
        self._foreign_structures_gateway = foreign_structures_gateway
        self._inventory_locations_gateway = inventory_locations_gateway

    def assets_tree(self) -> Dict[str, AssetTreeItem]:
        corp_assets_data = self._corp_assets_gateway.assets()
        foreign_structures_data = self._foreign_structures_gateway.structures(
            corp_assets_data=corp_assets_data,
            corporation_name=self._corporation_name
        )
        sde_inv_items = self._inventory_locations_gateway.get_inventory_locations()

        return get_assets_tree(
            corp_assets_data=corp_assets_data,
            foreign_structures_data=foreign_structures_data,
            sde_inv_items=sde_inv_items,
            virtual_hierarchy_by_corpsag=True
        )
