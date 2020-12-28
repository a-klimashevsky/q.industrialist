import yaml
from rx import Observable, operators as ops

from app.controllers import SoldContractsForPeriodController
from app.domain import SoldContractsForPeriodUseCase
from app.utils import destruct_tuple


class SoldContractsForPeriodDiscordRenderer:

    def __init__(self,
                 controller: SoldContractsForPeriodController,
                 ):
        self._controller = controller

    def render(self) -> Observable:
        return self._controller.view_model().pipe(
            ops.map(destruct_tuple(lambda contracts, corp_name, time_period:
                                   (self._dump_contracts(contracts), corp_name, time_period))),
            ops.map(destruct_tuple(
                lambda content, corp_name, time_period: template.format(
                    content=content,
                    corp_name=corp_name,
                    period=str(time_period)
                )
            )),
            # ops.map(lambda content: template.format(content=content, corp_name="R Initiative 4", period="2 days")),
        )

    @staticmethod
    def _dump_contracts(contracts):
        return yaml.dump(contracts, allow_unicode=True, sort_keys=False)


template = """
@here
```yaml
corporation: {corp_name}
for period: {period}
{content}
```
"""
