from dataclasses import dataclass
from typing import List


@dataclass
class Auth:
    access_token: str
    refresh_token: str
    expired: int
    character_id: str
    character_name: str
    client_id: str
    scope: List[str]
