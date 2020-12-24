from dataclasses import dataclass


@dataclass
class LocationInfo:
    region_id: int
    region_name: str
    name: str
    foreign: bool
