from abc import abstractmethod, ABC
from typing import Callable

from rx import Observable


class AuthUser(ABC, Callable):
    @abstractmethod
    def __call__(self) -> Observable:
        pass
