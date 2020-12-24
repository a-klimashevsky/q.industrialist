from dependency_injector import containers, providers

from app.esi.esi_container import EsiContainer
from app.sde.sde_container import SdeContainer
from app.controllers.controllers_container import ControllersContainer
from app.domain import DomainContainer
from app.renderers.renderers_container import RenderersContainer


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    sde = providers.Container(
        SdeContainer,
        cache_dir=config.cache_dir,
        character_name=config.character_name,
    )

    esi = providers.Container(
        EsiContainer,
        cache_dir=config.cache_dir,
        offline_mode=config.offline_mode,
        character_name=config.character_name,
    )

    domain = providers.Container(
        DomainContainer,
        type_info_gateway=sde.type_info_gateway,
        market_group_gateway=sde.market_group_gateway,
        market_price_gateway=esi.market_price_gateway,
        corp_assets_gateway=esi.corp_assets_gateway,
        foreign_structures_gateway=esi.foreign_structures_gateway,
        inventory_locations_gateway=sde.inventory_locations_gateway,
        inventory_names_gateway=sde.inventory_names_gateway,
        corp_assets_names_gateway=esi.corp_assets_names_gateway
    )

    controllers = providers.Container(
        ControllersContainer,
        corp_assets_service=domain.corp_assets_service,
        type_info_service=domain.type_info_service,
        market_groups_service=domain.market_group_service,
        market_price_service=domain.market_price_service,
        location_info_service=domain.location_info_service,
    )

    renderers = providers.Container(
        RenderersContainer,
        assets_tree_controller=controllers.assets_tree_controller,
        cache_dir=config.cache_dir
    )
