from dataclasses import dataclass
from typing import List

from eve.viewmodels import AssetTreeItemViewModel


@dataclass
class CorpAssetsViewModel:
    roots: List[AssetTreeItemViewModel]
