from datetime import datetime, timedelta

import pytz
from rx import Observable, operators as ops
from rx import from_list

from app.domain import ContractService, ContractInfo
from app.domain.gateways import GetCustomStructureInfo, GetCorporationContracts

utc = pytz.UTC


class ContractServiceImpl(ContractService):

    def __init__(self,
                 get_corp_contracts: GetCorporationContracts,
                 get_custom_structure_info: GetCustomStructureInfo
                 ):
        self._get_custom_structure_info = get_custom_structure_info
        self._get_corp_contracts = get_corp_contracts
        pass

    def get(self) -> Observable:
        return self._get_corp_contracts().pipe(
            ops.flat_map(lambda it: from_list(it)),
            ops.filter(lambda info: info.for_corporation),
            ops.filter(lambda info: info.issuer_corporation_id == 98615601),
            ops.filter(lambda info: info.type == "item_exchange"),
            ops.filter(lambda info: info.status == "finished"),
            ops.filter(lambda info: len(info.title) > 0),
            ops.filter(lambda info: _filter_by_date(info)),
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


TIME_DELTA = timedelta(days=2)


def _filter_by_date(info: ContractInfo) -> bool:
    datelimit = datetime.today() - TIME_DELTA
    datelimit = utc.localize(datelimit)
    return info.date_completed > datelimit
