from rx import Observable
from rx import operators as ops

from app.domain import CharacterInfo
from app.domain.gateways import AuthUser
from app.domain.gateways.get_character_info import GetCharacterInfo

from eve_esi_interface import EveOnlineInterface


class GetCharacterInfoImpl(GetCharacterInfo):

    def __init__(self,
                 auth_user: AuthUser,
                 eve_interface: EveOnlineInterface,
                 ):
        self._auth_user = auth_user
        self._eve_interface = eve_interface

    def __call__(self) -> Observable:
        return self._auth_user().pipe(
            ops.map(lambda auth: self._eve_interface.get_esi_data(
                "characters/{}/".format(auth.character_id),
                fully_trust_cache=True)
                    ),
            ops.map(
                lambda data: CharacterInfo(**data)
            )
        )
        pass
