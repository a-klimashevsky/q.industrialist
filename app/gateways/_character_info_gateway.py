from abc import abstractmethod, ABC

from app.domain.character_info import CharacterInfo
from eve_esi_interface import EveOnlineInterface


class CharacterInfoGateway(ABC):
    @abstractmethod
    def info(self, name: str) -> CharacterInfo:
        pass


class CharacterInfoGatewayImpl(CharacterInfoGateway):
    _eve_interface: EveOnlineInterface

    def __init__(self,
                 eve_interface: EveOnlineInterface
                 ):
        self._eve_interface = eve_interface
        pass

    def info(self, name: str) -> CharacterInfo:
        auths = self._eve_interface.authenticate(name)
        character_id = auths["character_id"]
        character_name = auths["character_name"]

        character_data = self._eve_interface.get_esi_data(
            "characters/{}/".format(character_id),
            fully_trust_cache=True)
        corporation_id = character_data["corporation_id"]

        return CharacterInfo(
            character_id=character_id,
            character_name=character_name,
            corporation_id=corporation_id,
        )
