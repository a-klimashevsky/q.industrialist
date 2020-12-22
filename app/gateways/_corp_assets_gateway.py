from typing import List

from app.domain import Asset
from app.gateways import CharacterInfoGateway
from eve_esi_interface import EveOnlineInterface


# TODO (a.klimashevsky): extract implementation
class CorpAssetsGateway:
    _eve_interface: EveOnlineInterface
    _character_info_gateway: CharacterInfoGateway
    _character_name: str
    _cache = None

    def __init__(self, eve_interface: EveOnlineInterface,
                 character_info_gateway: CharacterInfoGateway,
                 character_name: str,
                 ):
        self._eve_interface = eve_interface
        self._character_info_gateway = character_info_gateway
        self._character_name = character_name
        pass

    def assets(self) -> List[Asset]:
        if self._cache is None:
            character_info = self._character_info_gateway.info(self._character_name)
            url = "corporations/{}/assets/".format(character_info.corporation_id)
            data = self._eve_interface.get_esi_paged_data(url)
            self._cache = [Asset.from_dict(x) for x in data]
        return self._cache
