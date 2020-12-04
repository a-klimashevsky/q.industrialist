from abc import ABC, abstractmethod

from eve.viewmodels import AssetTreeItemViewModel


class AssetsTreeController(ABC):
    @abstractmethod
    def tree(self) -> AssetTreeItemViewModel:
        pass
