from abc import abstractmethod, ABC
from typing import Dict

from app.domain import MarketGroup


class MarketGroupsGateway(ABC):

    @abstractmethod
    def market_groups(self) -> Dict[int, MarketGroup]:
        pass
