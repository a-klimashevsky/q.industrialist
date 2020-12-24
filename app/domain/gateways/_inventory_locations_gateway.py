from abc import abstractmethod, ABC
from typing import Dict

from app.domain import InventoryLocation


class InventoryLocationGateway(ABC):

    @abstractmethod
    def get_inventory_locations(self) -> Dict[int, InventoryLocation]:
        pass
