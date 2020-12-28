from dependency_injector import containers, providers
from dependency_injector.providers import Provider

from app.domain import TypeInfoService, TypeInfoServiceImpl, MarketGroupService, MarketGroupServiceImpl, \
    MarketPriceServiceImpl, SoldContractsForPeriodUseCase
from app.domain._assets_service_impl import CorpAssetsServiceImpl
from app.domain._contracts_service_impl import ContractServiceImpl
from app.domain._location_info_service import LocationInfoServiceImpl


class DomainContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    type_info_gateway = providers.Dependency()
    market_group_gateway = providers.Dependency()
    market_price_gateway = providers.Dependency()
    corp_assets_gateway = providers.Dependency()
    foreign_structures_gateway = providers.Dependency()
    inventory_locations_gateway = providers.Dependency()
    inventory_names_gateway = providers.Dependency()
    corp_assets_names_gateway = providers.Dependency()

    get_corp_contracts = providers.Dependency()
    get_custom_structure_info = providers.Dependency()

    type_info_service = providers.Singleton(
        TypeInfoServiceImpl,
        type_info_gateway=type_info_gateway
    )

    market_group_service = providers.Singleton(
        MarketGroupServiceImpl,
        gateway=market_group_gateway
    )

    market_price_service = providers.Singleton(
        MarketPriceServiceImpl,
        gateway=market_price_gateway
    )

    corp_assets_service = providers.Singleton(
        CorpAssetsServiceImpl,
        corporation_name=config.corporation_name,
        corp_assets_gateway=corp_assets_gateway,
        foreign_structures_gateway=foreign_structures_gateway,
        inventory_locations_gateway=inventory_locations_gateway
    )

    location_info_service = providers.Singleton(
        LocationInfoServiceImpl,
        inventory_names_gateway=inventory_names_gateway,
        inventory_location_gateway=inventory_locations_gateway,
        corp_assets_names_gateway=corp_assets_names_gateway,
        corp_assets_gateway=corp_assets_gateway,
        foreign_structures_gateway=foreign_structures_gateway,
    )

    contracts_service = providers.Singleton(
        ContractServiceImpl,
        get_corp_contracts=get_corp_contracts,
        get_custom_structure_info=get_custom_structure_info
    )

    sold_contracts_for_period: Provider[SoldContractsForPeriodUseCase] = contracts_service
