from dependency_injector import containers, providers

from ._character_info_gateway_impl import CharacterInfoGatewayImpl
from ._corp_assets_gateway_impl import CorpAssetsGatewayImpl
from ._foreign_structures_gateway_impl import ForeignStructuresGatewayImpl
from ._get_corp_assets_names_impl import CorpAssetsNamesGatewayImpl
from ._market_prices_gateway_impl import MarketPricesGatewayImpl
from ._create_esi_interface import _create_esi_interface


class EsiContainer(containers.DeclarativeContainer):
    cache_dir = providers.Dependency()
    character_name = providers.Dependency()
    offline_mode = providers.Dependency()

    eve_interface = providers.Singleton(
        _create_esi_interface,
        cache_dir=cache_dir,
        offline_mode=offline_mode
    )

    character_info_gateway = providers.Singleton(
        CharacterInfoGatewayImpl,
        eve_interface=eve_interface,
    )

    corp_assets_gateway = providers.Singleton(
        CorpAssetsGatewayImpl,
        eve_interface=eve_interface,
        character_name=character_name,
        character_info_gateway=character_info_gateway,
    )

    foreign_structures_gateway = providers.Singleton(
        ForeignStructuresGatewayImpl,
        eve_interface=eve_interface
    )

    corp_assets_names_gateway = providers.Singleton(
        CorpAssetsNamesGatewayImpl,
        eve_interface=eve_interface,
        character_name=character_name,
        character_info_gateway=character_info_gateway,
    )

    market_price_gateway = providers.Singleton(
        MarketPricesGatewayImpl,
        eve_interface=eve_interface,
    )
