from dependency_injector import containers, providers

from ._inventory_location_names_impl import InventoryLocationNamesGatewayImpl
from ._inventory_locations_gateway_impl import InventoryLocationGatewayImpl
from ._markets_groups_impl import MarketGroupsGatewayImpl
from ._type_info_gateway_impl import TypeInfoGatewayImpl


class SdeContainer(containers.DeclarativeContainer):
    cache_dir = providers.Dependency()
    character_name = providers.Dependency()

    inventory_names_gateway = providers.Singleton(
        InventoryLocationNamesGatewayImpl,
        cache_dir=cache_dir
    )

    inventory_locations_gateway = providers.Singleton(
        InventoryLocationGatewayImpl,
        cache_dir=cache_dir
    )

    market_group_gateway = providers.Singleton(
        MarketGroupsGatewayImpl,
        cache_dir=cache_dir,
    )

    type_info_gateway = providers.Singleton(
        TypeInfoGatewayImpl,
        cache_dir=cache_dir
    )

