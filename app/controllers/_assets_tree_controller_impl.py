from typing import Optional, Dict, List

import eve_esi_tools
import eve_sde_tools
import q_industrialist_settings
from app.controllers import AssetsTreeController
from app.domain import CorpAssetsService, AssetTreeItem, TypeInfoService, MarketGroup, MarketGroupService, \
    MarketPriceService
from app.domain._location_info_service import LocationInfoService
from app.domain.get_basis_market_group_by_type_id import get_basis_market_group_by_type_id
from app.domain.get_item_name_by_type_id import get_item_name_by_type_id
from app.viewmodels import AssetTreeItemViewModel, CorpAssetsViewModel


class AssetsTreeControllerImpl(AssetsTreeController):
    _corp_assets_service: CorpAssetsService
    _type_info_service: TypeInfoService
    _market_groups_service: MarketGroupService
    _market_price_service: MarketPriceService
    _location_info_service: LocationInfoService

    def __init__(self,
                 corp_assets_service: CorpAssetsService,
                 type_info_service: TypeInfoService,
                 market_groups_service: MarketGroupService,
                 market_price_service: MarketPriceService,
                 location_info_service: LocationInfoService,
                 ):
        self._corp_assets_service = corp_assets_service
        self._type_info_service = type_info_service
        self._market_groups_service = market_groups_service
        self._market_price_service = market_price_service
        self._location_info_service = location_info_service
        pass

    def tree(self) -> List[AssetTreeItemViewModel]:
        data = self._corp_assets_service.all()
        models = []
        for item in data.roots:
            model = self._build(data.tree[str(item)], data)
            models.append(model)
        return models

    def _build(self, asset: AssetTreeItem, data) -> AssetTreeItemViewModel:

        type_id = asset.type_id

        types = self._type_info_service.all()

        market_groups = self._market_groups_service.all()
        market_group_name = self._get_market_group_name(types, market_groups, type_id)

        market_prices_data = self._market_price_service.all()

        icon_url = self._get_img_src(type_id=type_id, size=32)
        name = get_item_name_by_type_id(types, type_id)
        market_price = market_prices_data.get(type_id, None)

        quantity = asset.quantity
        base_price: Optional[float] = None
        volume: Optional[float] = None

        location_info = self._location_info_service.get_into(asset.item_id)

        if type_id in types:
            __type_dict = types[type_id]
            if __type_dict.basePrice:
                base_price = __type_dict.basePrice * quantity
            if __type_dict.volume:
                volume = __type_dict.volume * quantity
        view_model = AssetTreeItemViewModel(
            item_id=str(asset.item_id),
            item_name=name,
            item_icon_url=icon_url,
            location_type=asset.location_flag,
            quantity=quantity,
            children_count=len(asset.items),
            market_group=market_group_name,
            base_price=base_price,
            average_price=None if market_price is None else market_price.average_price * quantity,
            adjusted_price=None if market_price is None else market_price.adjusted_price * quantity,
            volume=volume,
            foreign = location_info.foreign,
            location_name = location_info.name
        )

        for child in asset.items:
            try:
                child_view_model = self._build(data.tree[str(child)], data)
                view_model.add_children(child_view_model)
            except  KeyError:
                pass


        return view_model

    @staticmethod
    def _get_market_group_name(types, market_groups, type_id):
        group_id = get_basis_market_group_by_type_id(types, market_groups, type_id)
        if group_id == None:
            return None
        market_group_name = market_groups[group_id].name["en"]
        return market_group_name

    # TODO: fix it. move to controller
    @staticmethod
    def _get_img_src(type_id: int, size: int):
        if q_industrialist_settings.g_use_filesystem_resources:
            return 'image_export_collection/Types/{}_{}.png'.format(type_id, size)
        else:
            return 'http://imageserver.eveonline.com/Type/{}_{}.png'.format(type_id, size)
