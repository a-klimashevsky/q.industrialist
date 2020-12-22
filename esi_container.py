from dependency_injector import containers, providers

from create_esi_interface import create_esi_interface


class EsiContainer(containers.DeclarativeContainer):

    cache_dir = providers.Dependency()
    offline_mode = providers.Dependency()

    interface = providers.Singleton(
        create_esi_interface,
        cache_dir=cache_dir,
        offline_mode=offline_mode
    )
