from typing import List, Callable


class AssetTreeItemViewModel:
    item_id: str
    item_name: str
    item_icon_url: str
    location_type: str
    count: int
    parent_id: str
    type: str
    base_price: str
    average_price: str
    adjusted_price: str
    volume: str

    def __init__(self,
                 item_id: str,
                 item_name: str,
                 item_icon_url: str,
                 location_type: str,
                 count: int,
                 type: str,
                 base_price: str = None,
                 average_price: str = None,
                 adjusted_price: str = None,
                 volume: str = None,
                 ):
        self.item_id = item_id
        self.item_name = item_name
        self.item_icon_url = item_icon_url
        self.location_type = location_type
        self.count = count
        self.type = type
        self.base_price = base_price
        self.average_price = average_price
        self.adjusted_price = adjusted_price
        self.volume = volume
        self.children: List[AssetTreeItemViewModel] = []

    def add_children(self, child: 'AssetTreeItemViewModel'):
        self.children.append(child)
        child.parent_id = self.item_id

    def print(self, visitor: Callable[['AssetTreeItemViewModel'], None]) -> None:
        visitor(self)
        for child in self.children:
            child.print(visitor)
