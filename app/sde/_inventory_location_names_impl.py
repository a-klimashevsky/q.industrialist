from typing import Dict

import eve_sde_tools
from app.domain.gateways import InventoryLocationNamesGateway


class InventoryLocationNamesGatewayImpl(InventoryLocationNamesGateway):
    _cache_dir: str

    _cache = None

    def __init__(self, cache_dir: str):
        self._cache_dir = cache_dir

    def names(self) -> Dict[int, str]:
        if self._cache is None:
            self._cache = self._names()
        return self._cache

    def _names(self) -> Dict[int, str]:
        data: Dict[str, str] = eve_sde_tools.read_converted(self._cache_dir, "invNames")
        return {int(k): v for k, v in data.items()}
