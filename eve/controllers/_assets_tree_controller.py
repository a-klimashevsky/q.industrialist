from abc import ABC, abstractmethod
from typing import List

from eve.viewmodels import CorpAssetsViewModel, AssetTreeItemViewModel


class AssetsTreeController(ABC):
    @abstractmethod
    def tree(self) -> List[AssetTreeItemViewModel]:
        pass
