from typing import List

from eve.domain import Asset
from eve_esi_interface import EveOnlineInterface


# TODO (a.klimashevsky): extract implementation
class CorpAssetsGateway:
    _eve_interface: EveOnlineInterface
    _corporation_id: int

    _cache = None

    def __init__(self, eve_interface: EveOnlineInterface, corporation_id: int):
        self._eve_interface = eve_interface
        self._corporation_id = corporation_id
        pass

    def assets(self) -> List[Asset]:
        if self._cache is None:
            url = "corporations/{}/assets/".format(self._corporation_id)
            data = self._eve_interface.get_esi_paged_data(url)
            self._cache = [Asset.from_dict(x) for x in data]
        return self._cache
