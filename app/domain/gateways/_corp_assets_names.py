from abc import abstractmethod, ABC
from typing import List

from app.domain import AssetName, Asset


class CorpAssetsNamesGateway(ABC):

    @abstractmethod
    def asets_name(self, corp_assets_data: List[Asset]) -> List[AssetName]:
        pass
