from rx import operators as ops, Observable

from app.domain import CustomStructureInfo
from app.domain.gateways import GetCustomStructureInfo
from app.domain.gateways import AuthUser

from eve_esi_interface import EveOnlineInterface


class GetCustomStructureInfoImpl(GetCustomStructureInfo):
    _eve_interface: EveOnlineInterface

    def __init__(self,
                 eve_interface: EveOnlineInterface,
                 auth_user: AuthUser
                 ):
        self._eve_interface = eve_interface
        self._auth_user = auth_user

    def __call__(self, structure_id: int) -> Observable:
        path = "universe/structures/{}/".format(structure_id)
        return self._auth_user().pipe(
            ops.map(lambda _: self._eve_interface.get_esi_data(path)),
            ops.map(lambda data: CustomStructureInfo(**data))
        )
