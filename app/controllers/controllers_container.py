from dependency_injector import containers, providers

from app.controllers._assets_tree_controller_impl import AssetsTreeControllerImpl
from app.controllers._sold_contracts_for_period_controller import SoldContractsForPeriodController


class ControllersContainer(containers.DeclarativeContainer):
    corp_assets_service = providers.Dependency()
    type_info_service = providers.Dependency()
    market_groups_service = providers.Dependency()
    market_price_service = providers.Dependency()
    location_info_service = providers.Dependency()

    sold_contracts_for_period = providers.Dependency()
    get_corp_info = providers.Dependency()

    time_period = providers.Dependency()

    assets_tree_controller = providers.Singleton(
        AssetsTreeControllerImpl,
        corp_assets_service=corp_assets_service,
        type_info_service=type_info_service,
        market_groups_service=market_groups_service,
        market_price_service=market_price_service,
        location_info_service=location_info_service
    )

    sold_contracts_for_period_controller = providers.Factory(
        SoldContractsForPeriodController,
        sold_contracts_for_period=sold_contracts_for_period,
        get_corp_info = get_corp_info,
        time_period=time_period,
    )
