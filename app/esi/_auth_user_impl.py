from rx import Observable
from rx import operators as ops, from_callable

from app.domain import Auth
from app.domain.gateways import AuthUser
from eve_esi_interface import EveOnlineInterface


class AuthUserImpl(AuthUser):

    def __init__(self,
                 eve_interface: EveOnlineInterface,
                 character_name: str,
                 ):
        self._eve_interface = eve_interface
        self._name = character_name

    def __call__(self) -> Observable:
        return from_callable(lambda: self._eve_interface.authenticate(self._name)).pipe(
            ops.map(lambda it: Auth(**it))
        )
