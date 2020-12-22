from abc import ABC, abstractmethod

from eve.domain import CorpAssets


class CorpAssetsService(ABC):

    @abstractmethod
    def all(self) -> CorpAssets:
        pass
