import yaml
from rx import Observable, operators as ops

from app.domain import SoldContractsForPeriodUseCase


class SoldContractsForPeriodDiscordRenderer:

    def __init__(self,
                 sold_contracts_for_period: SoldContractsForPeriodUseCase
                 ):
        self._sold_contracts_for_period = sold_contracts_for_period

    def render(self) -> Observable:
        return self._sold_contracts_for_period.get().pipe(
            ops.map(lambda it: yaml.dump(it, allow_unicode=True, sort_keys=False)),
            ops.map(lambda content: template.format(content=content, corp_name="R Initiative 4", period="2 days")),
        )


template = """
@here
```yaml
corporation: {corp_name}
for period: {period}
{content}
```
"""
