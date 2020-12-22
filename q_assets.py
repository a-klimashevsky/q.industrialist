﻿""" Q.Assets (desktop/mobile)

Prerequisites:
    * Have a Python 3 environment available to you (possibly by using a
      virtual environment: https://virtualenv.pypa.io/en/stable/).
    * Run pip install -r requirements.txt with this directory as your root.

    * Copy q_industrialist_settings.py.template into q_industrialist_settings.py and
      mood for your needs.
    * Create an SSO application at developers.eveonline.com with the scopes
      from g_client_scope list declared in q_industrialist_settings.py and the
      callback URL "https://localhost/callback/".
      Note: never use localhost as a callback in released applications.

To run this example, make sure you have completed the prerequisites and then
run the following command from this directory as the root:

>>> python eve_sde_tools.py --cache_dir=~/.q_industrialist
>>> python q_assets.py --pilot1="Qandra Si" --pilot2="Your Name" --online --cache_dir=~/.q_industrialist

Requires application scopes:
    * esi-assets.read_corporation_assets.v1 - Requires role(s): Director
    * esi-universe.read_structures.v1 - Requires: access token
"""
import sys

import requests
from dependency_injector.wiring import inject, Provide

import eve_esi_interface as esi

import eve_sde_tools
import console_app
import q_industrialist_settings

from __init__ import __version__
from application_container import ApplicationContainer
from eve.controllers import AssetsTreeController
from eve.renderers.assets_renderer import AssetsRenderer


@inject
def main(
        assets_tree_controller: AssetsTreeController = Provide[
            ApplicationContainer.controllers.assets_tree_controller
        ]
):
    p = console_app.get_argv_prms()
    c = p["workspace_cache_files_dir"]

    renderer = AssetsRenderer()

    renderer.render(assets_tree_controller.tree(), c)

    # Вывод в лог уведомления, что всё завершилось (для отслеживания с помощью tail)
    print("\nDone")


if __name__ == "__main__":
    argv_prms = console_app.get_argv_prms()

    cache_dir = argv_prms["workspace_cache_files_dir"]
    corporation_id = 98615601

    # настройка Eve Online ESI Swagger interface
    auth = esi.EveESIAuth(
        '{}/auth_cache'.format(cache_dir),
        debug=True)
    client = esi.EveESIClient(
        auth,
        debug=False,
        logger=True,
        user_agent='Q.Industrialist v{ver}'.format(ver=__version__))
    interface = esi.EveOnlineInterface(
        client,
        q_industrialist_settings.g_client_scope,
        cache_dir='{}/esi_cache'.format(cache_dir),
        offline_mode=argv_prms["offline_mode"])

    eve_interface = interface

    app_container = ApplicationContainer()
    app_container.config.from_dict(
        {
            'cache_dir': cache_dir,
            'corporation_id': corporation_id,
            'eve_interface': eve_interface,
            'corporation_name': 'R Initiative 4'
        },
    )
    app_container.wire(modules=[sys.modules[__name__]])

    main()
