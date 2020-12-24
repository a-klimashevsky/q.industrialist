from abc import abstractmethod, ABC
from typing import Dict

from app.domain import MarketGroup
from app.domain.gateways import MarketGroupsGateway


class MarketGroupService(ABC):
    @abstractmethod
    def all(self) -> Dict[int, MarketGroup]:
        pass


class MarketGroupServiceImpl(MarketGroupService):
    _gateway: MarketGroupsGateway
    _cache = None
    def __init__(self,
                 gateway: MarketGroupsGateway
                 ):
        self._gateway = gateway

    def all(self) -> Dict[int, MarketGroup]:
        if (self._cache is None):
            self._cache = self._gateway.market_groups()
        return self._cache
