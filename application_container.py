from dependency_injector import containers, providers

from esi_container import EsiContainer
from eve.controllers.controllers_container import ControllersContainer
from eve.domain import DomainContainer
from eve.gateways.gateways_container import GatewaysContainer


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    esi = providers.Container(
        EsiContainer,
        cache_dir=config.cache_dir,
        offline_mode=config.offline_mode,
    )

    gateway = providers.Container(
        GatewaysContainer,
        cache_dir=config.cache_dir,
        eve_interface=esi.interface,
        corporation_id=config.corporation_id,
    )

    domain = providers.Container(
        DomainContainer,
        type_info_gateway=gateway.type_info_gateway,
        market_group_gateway=gateway.market_group_gateway,
        market_price_gateway=gateway.market_price_gateway,
        corp_assets_gateway=gateway.corp_assets_gateway,
        foreign_structures_gateway=gateway.foreign_structures_gateway,
        inventory_locations_gateway=gateway.inventory_locations_gateway,
        inventory_names_gateway=gateway.inventory_names_gateway,
        corp_assets_names_gateway=gateway.corp_assets_names_gateway
    )

    controllers = providers.Container(
        ControllersContainer,
        corp_assets_service=domain.corp_assets_service,
        type_info_service=domain.type_info_service,
        market_groups_service=domain.market_group_service,
        market_price_service=domain.market_price_service,
        location_info_service=domain.location_info_service,
    )
