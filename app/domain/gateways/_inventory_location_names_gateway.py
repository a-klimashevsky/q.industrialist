from abc import abstractmethod, ABC
from typing import Dict


class InventoryLocationNamesGateway(ABC):

    @abstractmethod
    def names(self) -> Dict[int, str]:
        pass
