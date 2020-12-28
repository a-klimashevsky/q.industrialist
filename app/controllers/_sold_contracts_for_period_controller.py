from datetime import timedelta
from rx import Observable, combine_latest, operators as ops
import copy

from app.domain import SoldContractsForPeriodUseCase
from app.domain.gateways import GetCorporationInfo
from app.domain.gateways.get_character_info import GetCharacterInfo
from app.utils import destruct_tuple


class SoldContractsForPeriodController:

    def __init__(self,
                 sold_contracts_for_period: SoldContractsForPeriodUseCase,
                 get_corp_info: GetCorporationInfo,
                 time_period: timedelta
                 ):
        self._sold_contracts_for_period = sold_contracts_for_period
        self._get_corp_info = get_corp_info
        self._time_period = time_period

    def view_model(self) -> Observable:
        return combine_latest(
            self._sold_contracts_for_period.get(),
            self._get_corp_info()
        ).pipe(
            ops.map(destruct_tuple(lambda contracts, corp_info: (contracts, corp_info.name, self._time_period)))
        )
