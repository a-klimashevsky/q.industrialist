from typing import Optional

from attr import dataclass


@dataclass
class CorporationInfo:
    alliance_id: int
    ceo_id: int
    creator_id: int
    date_founded: str
    description: str
    home_station_id: int
    member_count: int
    name: str
    shares: int
    tax_rate: float
    ticker: str
    url: str
    war_eligible: bool
    faction_id: Optional[int] = None
