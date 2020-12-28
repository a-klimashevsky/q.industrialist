from rx import Observable, operators as ops

from app.domain import CorporationInfo
from app.domain.gateways import GetCorporationInfo
from app.domain.gateways.get_character_info import GetCharacterInfo

from eve_esi_interface import EveOnlineInterface


class GetCorporationInfoImpl(GetCorporationInfo):

    def __init__(self,
                 eve_interface: EveOnlineInterface,
                 get_character_info: GetCharacterInfo,
                 ):
        self._eve_interface = eve_interface
        self._get_character_info = get_character_info

    def __call__(self) -> Observable:
        return self._get_character_info().pipe(
            ops.map(lambda info: "corporations/{}/".format(info.corporation_id)),
            ops.map(lambda path: self._eve_interface.get_esi_data(
                path,
                fully_trust_cache=True)
                    ),
            ops.map(lambda it: CorporationInfo(**it))
        )
