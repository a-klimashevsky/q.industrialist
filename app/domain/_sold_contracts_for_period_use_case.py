from abc import abstractmethod, ABC
from rx import Observable


class SoldContractsForPeriodUseCase(ABC):

    @abstractmethod
    def get(self) -> Observable:
        pass
