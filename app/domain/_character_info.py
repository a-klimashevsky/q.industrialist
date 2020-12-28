from dataclasses import dataclass


@dataclass
class CharacterInfo:
    #character_id: int
   # character_name: str
    corporation_id: int
    alliance_id: int
    ancestry_id: int
    birthday: str
    bloodline_id: int
    description: str
    gender: str
    name: str
    race_id: int
    security_status: float
