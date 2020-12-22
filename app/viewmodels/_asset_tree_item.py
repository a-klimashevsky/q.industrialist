from typing import List, Callable


class AssetTreeItemViewModel:
    item_id: str
    item_name: str
    item_icon_url: str
    location_type: str
    quantity: int
    children_count: int
    parent_id: str = None
    market_group: str
    base_price: float
    average_price: float
    adjusted_price: float
    volume: float
    foreign: bool
    location_name: str

    def __init__(self,
                 item_id: str,
                 item_name: str,
                 item_icon_url: str,
                 location_type: str,
                 quantity: int,
                 children_count: int,
                 market_group: str,
                 base_price: float = None,
                 average_price: float = None,
                 adjusted_price: float = None,
                 volume: float = None,
                 foreign: bool = False,
                 location_name: str = None
                 ):
        self.item_id = item_id
        self.item_name = item_name
        self.item_icon_url = item_icon_url
        self.location_type = location_type
        self.quantity = quantity
        self.children_count = children_count
        self.market_group = market_group
        self.base_price = base_price
        self.average_price = average_price
        self.adjusted_price = adjusted_price
        self.volume = volume
        self.children: List[AssetTreeItemViewModel] = []
        self.foreign = foreign
        self.location_name = location_name

    def add_children(self, child: 'AssetTreeItemViewModel'):
        self.children.append(child)
        child.parent_id = self.item_id

    def print(self, visitor: Callable[['AssetTreeItemViewModel'], None]) -> None:
        visitor(self)
        for child in self.children:
            child.print(visitor)
