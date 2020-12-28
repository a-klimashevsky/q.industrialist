from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass
class ContractInfo:
    """
    General Contract details

    Args

    acceptor_id: int
      Who will accept the contract
    assignee_id: int
      ID to whom the contract is assigned, can be corporation or character ID
    availability: str
      To whom the contract is available
    collateral: float
      Collateral price (for Couriers only)
    contract_id: int
      contract_id integer
    date_accepted: str
      Date of confirmation of contract
    date_completed: str
      Date of completed of contract
    date_expired: str
      Expiration date of the contract
    date_issued: str
      Сreation date of the contract
    days_to_complete: int
      Number of days to perform the contract
    end_location_id: int
      End location ID (for Couriers contract)
    for_corporation: bool
      true if the contract was issued on behalf of the issuer’s corporation
    issuer_corporation_id: int
      Character’s corporation ID for the issuer
    issuer_id: int
      character ID for the issuer
    price: float
      Price of contract (for ItemsExchange and Auctions)
    reward: float
      Remuneration for contract (for Couriers only)
    start_location_id: int
      Start location ID (for Couriers contract)
    status: str
      Status of the the contract
    title: str
      Title of the contract
    type: str
      Type of the contract
    volume:
      Volume of items in the contract
"""

    acceptor_id: int
    assignee_id: int
    availability: str
    collateral: float
    contract_id: int
    date_expired: datetime
    date_issued: datetime
    days_to_complete: int
    end_location_id: int
    for_corporation: bool
    issuer_corporation_id: int
    issuer_id: int
    price: float
    reward: float
    start_location_id: int
    status: str
    title: str
    type: str
    volume: float
    buyout: float
    date_completed: datetime
    date_accepted: datetime
