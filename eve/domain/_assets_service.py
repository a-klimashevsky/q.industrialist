from abc import ABC, abstractmethod
from typing import Dict

from eve.domain import AssetsTree, AssetTreeItem


class AssetsService(ABC):

    @abstractmethod
    def assets_tree(self) -> Dict[str, AssetTreeItem]:
        pass
