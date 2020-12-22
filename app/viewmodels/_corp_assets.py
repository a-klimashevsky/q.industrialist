from dataclasses import dataclass
from typing import List

from app.viewmodels import AssetTreeItemViewModel


@dataclass
class CorpAssetsViewModel:
    roots: List[AssetTreeItemViewModel]
