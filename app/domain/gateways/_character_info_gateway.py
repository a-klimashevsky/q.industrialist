from abc import abstractmethod, ABC

from app.domain._character_info import CharacterInfo


class CharacterInfoGateway(ABC):
    @abstractmethod
    def info(self, name: str) -> CharacterInfo:
        pass
