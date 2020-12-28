from dataclasses import dataclass
from typing import Dict

import yaml


class ContractsStatisticsViewModel(yaml.YAMLObject):
    yaml_tag = u'!CorpContracts'

    def __init__(self,
                 name: str,
                 contracts: Dict[str, str]
                 ):
        self.__setattr__(u"Corporation Name", name)
        for contract in contracts:
            self.__setattr__(contract, contracts[contract])

