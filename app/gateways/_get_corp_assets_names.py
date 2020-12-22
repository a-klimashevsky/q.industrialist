import json
from typing import List, Dict

from app.domain import AssetName, Asset
from app.domain.get_assets_named_ids import get_assets_named_ids
from app.gateways import CharacterInfoGateway
from eve_esi_interface import EveOnlineInterface


class GetCorpAssetsNamesGateway:
    _eve_interface: EveOnlineInterface
    _character_info_gateway: CharacterInfoGateway
    _character_name: str
    _cache = None

    def __init__(self,
                 eve_interface: EveOnlineInterface,
                 character_info_gateway: CharacterInfoGateway,
                 character_name: str,
                 ):
        self._eve_interface = eve_interface
        self._character_info_gateway = character_info_gateway
        self._character_name = character_name
        pass

    def asets_name(self, corp_assets_data: List[Asset]) -> List[AssetName]:
        if self._cache is None:
            self._cache = self._asets_name(corp_assets_data)
        return self._cache

    def _asets_name(self, corp_assets_data: List[Asset]) -> List[AssetName]:
        ids = get_assets_named_ids(corp_assets_data)

        if len(ids) == 0: return []
        character_info = self._character_info_gateway.info(self._character_name)
        # Requires role(s): Director
        data = self._eve_interface.get_esi_data(
            "corporations/{}/assets/names/".format(character_info.corporation_id),
            json.dumps(ids, indent=0, sort_keys=False)
        )
        return [self._map_dict_to_asset_name(item) for item in data]

    @staticmethod
    def _map_dict_to_asset_name(item: Dict) -> AssetName:
        return AssetName(
            item_id=item.get("item_id", 0),
            name=item.get("name", "")
        )
