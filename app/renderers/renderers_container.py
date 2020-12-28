from dependency_injector import containers, providers

from app.renderers._sold_contracts_for_period_discord_renderer import SoldContractsForPeriodDiscordRenderer
from app.renderers.assets_renderer import AssetsRenderer


class RenderersContainer(containers.DeclarativeContainer):
    cache_dir = providers.Dependency()
    assets_tree_controller = providers.Dependency()

    sold_contracts_for_period_controller = providers.Dependency()

    assets_renderer = providers.Factory(
        AssetsRenderer,
        cache_dir=cache_dir,
        controller=assets_tree_controller
    )

    sold_contracts_for_period_discord_renderer = providers.Factory(
        SoldContractsForPeriodDiscordRenderer,
        controller=sold_contracts_for_period_controller,
    )
