from abc import ABC, abstractmethod
from typing import Callable
from rx import Observable

from app.domain._character_info import CharacterInfo


class GetCharacterInfo(ABC, Callable):

    @abstractmethod
    def __call__(self) -> Observable:
        pass
