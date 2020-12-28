from typing import Dict, List, Any

from app.domain import MarketPrice
from app.domain.gateways import MarketPricesGateway
from eve_esi_interface import EveOnlineInterface


class MarketPricesGatewayImpl(MarketPricesGateway):
    _eve_interface: EveOnlineInterface

    def __init__(self, eve_interface: EveOnlineInterface):
        self._eve_interface = eve_interface

    def market_prices(self) -> Dict[int, MarketPrice]:
        data: List[Dict] = self._eve_interface.get_esi_data("markets/prices/")
        prices = [self.map_dict_to_market_price(item) for item in data]
        return {price.type_id: price for price in prices}

    @staticmethod
    def map_dict_to_market_price(src: Dict[str, Any]):
        return MarketPrice(
            adjusted_price=src.get("adjusted_price", 0),
            average_price=src.get("average_price", 0),
            type_id=src.get("type_id", 0)
        )