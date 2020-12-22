from dependency_injector import containers, providers

from eve.renderers.assets_renderer import AssetsRenderer


class RenderersContainer(containers.DeclarativeContainer):
    cache_dir = providers.Dependency()
    assets_tree_controller = providers.Dependency()

    assets_renderer = providers.Factory(
        AssetsRenderer,
        cache_dir=cache_dir,
        controller = assets_tree_controller
    )
