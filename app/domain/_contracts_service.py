from abc import ABC

from app.domain import SoldContractsForPeriodUseCase


class ContractService(SoldContractsForPeriodUseCase, ABC):
    pass
