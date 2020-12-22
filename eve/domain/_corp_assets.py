from dataclasses import dataclass
from typing import List, Dict

from eve.domain import AssetTreeItem


@dataclass
class CorpAssets:
    roots: List[int]
    tree: Dict[str, AssetTreeItem]
