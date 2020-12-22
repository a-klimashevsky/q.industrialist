from dependency_injector import containers, providers

from eve.controllers._assets_tree_controller_impl import AssetsTreeControllerImpl


class ControllersContainer(containers.DeclarativeContainer):

    corp_assets_service = providers.Dependency()
    type_info_service = providers.Dependency()
    market_groups_service = providers.Dependency()
    market_price_service = providers.Dependency()
    location_info_service = providers.Dependency()

    assets_tree_controller = providers.Singleton(
        AssetsTreeControllerImpl,
        corp_assets_service=corp_assets_service,
        type_info_service=type_info_service,
        market_groups_service=market_groups_service,
        market_price_service=market_price_service,
        location_info_service = location_info_service
    )
