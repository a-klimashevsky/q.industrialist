from abc import abstractmethod, ABC
from typing import List

from app.domain import Asset


class CorpAssetsGateway(ABC):

    @abstractmethod
    def assets(self) -> List[Asset]:
        pass
