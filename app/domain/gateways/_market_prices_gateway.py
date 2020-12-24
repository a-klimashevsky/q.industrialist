from abc import abstractmethod, ABC
from typing import Dict

from app.domain import MarketPrice


class MarketPricesGateway(ABC):

    @abstractmethod
    def market_prices(self) -> Dict[int, MarketPrice]:
        pass
