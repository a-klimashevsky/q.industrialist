from abc import ABC, abstractmethod
from typing import Dict

from app.domain import MarketPrice
from app.gateways import MarketPricesGateway


class MarketPriceService(ABC):

    @abstractmethod
    def all(self) -> Dict[int, MarketPrice]:
        pass


class MarketPriceServiceImpl(MarketPriceService):
    _gateway: MarketPricesGateway
    _cache = None

    def __init__(self, gateway: MarketPricesGateway):
        self._gateway = gateway

    def all(self) -> Dict[int, MarketPrice]:
        if(self._cache is None):
            self._cache = self._gateway.market_prices()
        return self._cache
