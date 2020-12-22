from typing import Callable

from dependency_injector import containers, providers


from eve.gateways import TypeInfoGateway, MarketGroupsGateway, MarketPricesGateway, CorpAssetsGateway, \
    ForeignStructuresGateway, InventoryLocationGateway, GetInventoryLocationNamesGateway, GetCorpAssetsNamesGateway


class GatewaysContainer(containers.DeclarativeContainer):
    cache_dir = providers.Dependency()
    eve_interface = providers.Dependency()
    corporation_id = providers.Dependency()

    type_info_gateway: Callable[[], TypeInfoGateway] = providers.Singleton(
        TypeInfoGateway,
        cache_dir=cache_dir
    )
    market_group_gateway = providers.Singleton(
        MarketGroupsGateway,
        cache_dir=cache_dir,
    )
    market_price_gateway = providers.Singleton(
        MarketPricesGateway,
        eve_interface=eve_interface,
    )
    corp_assets_gateway = providers.Singleton(
        CorpAssetsGateway,
        eve_interface=eve_interface,
        corporation_id=corporation_id,
    )
    foreign_structures_gateway = providers.Singleton(
        ForeignStructuresGateway,
        eve_interface=eve_interface
    )
    inventory_locations_gateway = providers.Singleton(
        InventoryLocationGateway,
        cache_dir=cache_dir
    )

    inventory_names_gateway = providers.Singleton(
        GetInventoryLocationNamesGateway,
        cache_dir=cache_dir
    )
    corp_assets_names_gateway = providers.Singleton(
        GetCorpAssetsNamesGateway,
        eve_interface=eve_interface,
        corporation_id=corporation_id
    )
