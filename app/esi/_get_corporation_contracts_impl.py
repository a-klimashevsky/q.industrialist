from datetime import datetime
from typing import List, Dict, Any

from rx import Observable, operators as ops

from app.domain import ContractInfo
from app.domain.gateways import GetCorporationContracts
from app.domain.gateways.get_character_info import GetCharacterInfo
from eve_esi_interface import EveOnlineInterface


class GetCorporationContractsImpl(GetCorporationContracts):
    _eve_interface: EveOnlineInterface

    def __init__(self,
                 eve_interface: EveOnlineInterface,
                 get_character_info: GetCharacterInfo,
                 ):
        self._eve_interface = eve_interface
        self._get_character_info = get_character_info

    def __call__(self) -> Observable:
        return self._get_character_info().pipe(
            ops.map(lambda info: "corporations/{}/contracts/".format(info.corporation_id)),
            ops.map(lambda path: self._eve_interface.get_esi_paged_data(path)),
            ops.map(lambda data: [_map(item) for item in data])
        )

    pass


def _parse_datetime(value: str):
    if value is None:
        return None

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _map(item: Dict[str, Any]) -> ContractInfo:
    return ContractInfo(
        acceptor_id=item.get("acceptor_id", None),
        assignee_id=item.get("assignee_id", None),
        availability=item.get("availability", None),
        collateral=item.get("collateral", None),
        contract_id=item.get("contract_id", None),
        date_expired=_parse_datetime(item.get("date_expired", None)),
        date_issued=_parse_datetime(item.get("date_issued", None)),
        days_to_complete=item.get("days_to_complete", None),
        end_location_id=item.get("end_location_id", None),
        for_corporation=item.get("for_corporation", None),
        issuer_corporation_id=item.get("issuer_corporation_id", None),
        issuer_id=item.get("issuer_id", None),
        price=item.get("price", None),
        reward=item.get("reward", None),
        start_location_id=item.get("start_location_id", None),
        status=item.get("status", None),
        title=item.get("title", None),
        type=item.get("type", None),
        volume=item.get("volume", None),
        buyout=item.get("buyout", None),
        date_completed=_parse_datetime(item.get("date_completed", None)),
        date_accepted=_parse_datetime(item.get("date_accepted", None)),
    )
