import q_industrialist_settings
import eve_esi_interface as esi
from __init__ import __version__


def create_esi_interface(cache_dir, offline_mode):
    auth_cache_dir = '{}/auth_cache'.format(cache_dir)
    auth = esi.EveESIAuth(
        cache_dir=auth_cache_dir,
        debug=True
    )

    user_agent = 'Q.Industrialist v{ver}'.format(ver=__version__)

    client = esi.EveESIClient(
        auth_cache=auth,
        debug=False,
        logger=True,
        user_agent=user_agent
    )

    esi_interface_cache_dir = '{}/esi_cache'.format(cache_dir)

    interface = esi.EveOnlineInterface(
        client=client,
        scopes=q_industrialist_settings.g_client_scope,
        cache_dir=esi_interface_cache_dir,
        offline_mode=offline_mode
    )

    return interface
