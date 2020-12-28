from abc import ABC, abstractmethod
from typing import List, Callable

from app.domain import ContractInfo
from rx import Observable


class GetCorporationContracts(ABC, Callable):

    @abstractmethod
    def __call__(self) -> Observable:
        pass
