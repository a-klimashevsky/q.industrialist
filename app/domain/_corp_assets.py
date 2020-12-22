from dataclasses import dataclass
from typing import List, Dict

from app.domain import AssetTreeItem


@dataclass
class CorpAssets:
    roots: List[int]
    tree: Dict[str, AssetTreeItem]
