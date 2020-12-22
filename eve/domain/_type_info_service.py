from abc import abstractmethod, ABC
from typing import Dict

from eve.domain import TypeInfo
from eve.gateways import TypeInfoGateway


class TypeInfoService(ABC):

    @abstractmethod
    def all(self) -> Dict[int, TypeInfo]:
        pass


class TypeInfoServiceImpl(TypeInfoService):
    _type_info_gateway: TypeInfoGateway
    _cache = None

    def __init__(self,
                 type_info_gateway: TypeInfoGateway,
                 ):
        self._type_info_gateway = type_info_gateway

    def all(self) -> Dict[int, TypeInfo]:
        if(self._cache is None):
            self._cache = self._type_info_gateway.type_info()
        return self._cache
