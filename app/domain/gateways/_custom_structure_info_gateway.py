from abc import abstractmethod, ABC
from typing import Callable

from rx import Observable

from app.domain import CustomStructureInfo


class GetCustomStructureInfo(ABC, Callable):

    @abstractmethod
    def __call__(self, structure_id: int) -> Observable:
        pass
