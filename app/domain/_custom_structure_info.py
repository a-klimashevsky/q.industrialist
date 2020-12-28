from dataclasses import dataclass
from typing import Any


@dataclass
class CustomStructureInfo:
    name: str
    owner_id: int
    solar_system_id: int
    type_id: int
    position: Any
