from datetime import datetime, timedelta

import pytz
from rx import Observable, operators as ops
from rx import from_list

from app.domain import ContractService, ContractInfo
from app.domain.gateways import GetCustomStructureInfo, GetCorporationContracts
from app.domain.gateways.get_character_info import GetCharacterInfo

utc = pytz.UTC


class ContractServiceImpl(ContractService):

    def __init__(self,
                 get_character_info: GetCharacterInfo,
                 get_corp_contracts: GetCorporationContracts,
                 get_custom_structure_info: GetCustomStructureInfo,
                 time_period: timedelta
                 ):
        self._get_character_info = get_character_info
        self._get_custom_structure_info = get_custom_structure_info
        self._get_corp_contracts = get_corp_contracts
        self._time_period = time_period
        pass

    def get(self) -> Observable:
        return self._get_character_info().pipe(
            ops.flat_map(lambda info: self._get(info.corporation_id))
        )

    def _get(self, corporation_id) -> Observable:
        return self._get_corp_contracts().pipe(
            ops.flat_map(lambda it: from_list(it)),
            ops.filter(lambda info: info.for_corporation),
            ops.filter(lambda info: info.issuer_corporation_id == corporation_id),
            ops.filter(lambda info: info.type == "item_exchange"),
            ops.filter(lambda info: info.status == "finished"),
            ops.filter(lambda info: len(info.title) > 0),
            ops.filter(lambda info: self._filter_by_date(info)),
            ops.group_by(lambda info: info.start_location_id),
            ops.flat_map(lambda gpr: gpr.pipe(
                ops.group_by(lambda info: info.title),
                ops.flat_map(lambda sub_gpr: sub_gpr.pipe(
                    ops.to_list(),
                    ops.map(lambda it: len(it)),
                    ops.to_dict(lambda it: sub_gpr.key),
                )),
                ops.to_list(),
                ops.flat_map(lambda it: self._get_custom_structure_info(gpr.key)
                             .pipe(
                    ops.map(lambda info: {info.name: it}),
                )),
            )),
            ops.to_list(),
        )

    def _filter_by_date(self, info: ContractInfo) -> bool:
        datelimit = datetime.today() - self._time_period
        datelimit = utc.localize(datelimit)
        return info.date_completed > datelimit
