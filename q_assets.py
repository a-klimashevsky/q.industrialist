""" Q.Assets (desktop/mobile)

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

from dependency_injector.wiring import inject, Provide

import console_app
import eve_sde_tools
from application_container import ApplicationContainer
from app.controllers import AssetsTreeController
from app.renderers.assets_renderer import AssetsRenderer


@inject
def main(
        renderer: AssetsRenderer = Provide[
            ApplicationContainer.renderers.assets_renderer
        ]
):
    renderer.render()
    # Вывод в лог уведомления, что всё завершилось (для отслеживания с помощью tail)
    print("\nDone")


if __name__ == "__main__":
    argv_prms = console_app.get_argv_prms()

    cache_dir = argv_prms["workspace_cache_files_dir"]
    offline_mode = argv_prms["offline_mode"]
    character_name = argv_prms["character_names"][0]

    app_container = ApplicationContainer()

    app_container.config.from_dict(
        {
            'cache_dir': cache_dir,
            'offline_mode': offline_mode,
            'character_name': character_name,
        },
    )
    app_container.wire(modules=[sys.modules[__name__]])

    main()
