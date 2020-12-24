from abc import ABC, abstractmethod
from typing import Dict, List

from app.domain import Asset
from app.esi import StructureData


class ForeignStructuresGateway(ABC):

    @abstractmethod
    def structures(self, corp_assets_data: List[Asset]) -> Dict[str, StructureData]:
        pass
