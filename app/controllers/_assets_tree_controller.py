from abc import ABC, abstractmethod
from typing import List

from app.viewmodels import CorpAssetsViewModel, AssetTreeItemViewModel


class AssetsTreeController(ABC):
    @abstractmethod
    def tree(self) -> List[AssetTreeItemViewModel]:
        pass
