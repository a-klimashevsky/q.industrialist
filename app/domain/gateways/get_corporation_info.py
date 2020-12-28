from abc import ABC, abstractmethod
from typing import Callable

from rx import Observable


class GetCorporationInfo(ABC, Callable):

    @abstractmethod
    def __call__(self) -> Observable:
        pass
