from abc import abstractmethod, ABC
from typing import Dict

import eve_sde_tools
from app.domain import TypeInfo


class TypeInfoGateway(ABC):

    @abstractmethod
    def type_info(self) -> Dict[int, TypeInfo]:
        data: Dict[str, Dict] = eve_sde_tools.read_converted(self._cache_dir, "typeIDs")
        return {int(type_id): self._map_dict_to_type_info(type_id, info) for type_id, info in data.items()}
