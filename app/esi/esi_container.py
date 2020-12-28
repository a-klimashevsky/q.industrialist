from dependency_injector import containers, providers

from ._auth_user_impl import AuthUserImpl
from ._character_info_gateway_impl import CharacterInfoGatewayImpl
from ._corp_assets_gateway_impl import CorpAssetsGatewayImpl
from ._get_corporation_contracts_impl import GetCorporationContractsImpl
from ._foreign_structures_gateway_impl import ForeignStructuresGatewayImpl
from ._get_corp_assets_names_impl import CorpAssetsNamesGatewayImpl
from ._market_prices_gateway_impl import MarketPricesGatewayImpl
from ._create_esi_interface import _create_esi_interface
from ._get_custom_structure_info_impl import GetCustomStructureInfoImpl
from .get_character_info_impl import GetCharacterInfoImpl


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

    auth_user = providers.Singleton(
        AuthUserImpl,
        eve_interface=eve_interface,
        character_name=character_name,
    )

    get_character_info = providers.Singleton(
        GetCharacterInfoImpl,
        auth_user=auth_user,
        eve_interface=eve_interface,
    )

    get_corp_contracts = providers.Singleton(
        GetCorporationContractsImpl,
        eve_interface=eve_interface,
        get_character_info=get_character_info,
    )

    get_custom_structures_info = providers.Singleton(
        GetCustomStructureInfoImpl,
        auth_user=auth_user,
        eve_interface=eve_interface,
    )
