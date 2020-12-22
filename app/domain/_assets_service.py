from abc import ABC, abstractmethod

from app.domain import CorpAssets


class CorpAssetsService(ABC):

    @abstractmethod
    def all(self) -> CorpAssets:
        pass
