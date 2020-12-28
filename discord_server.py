import logging
import sys

from app.renderers._sold_contracts_for_period_discord_renderer import SoldContractsForPeriodDiscordRenderer

logger = logging.getLogger()

from rx import operators as ops
from dependency_injector.wiring import inject, Provide
from discord import Webhook, RequestsWebhookAdapter
from rx import Observable

import console_app
from application_container import ApplicationContainer

r4_hook = "https://discord.com/api/webhooks/791718372495851540/Da0xD8RjcsWusGDafwMM6igbqafTU3uFPOVRtzFm1mvop_LJTq1YwzncrXeI65zWxN5m"

my_hook = "https://discord.com/api/webhooks/791677044005928982/ZYWD0FWliiALSUGKrVgtr6prwbv1s_wdWZMSkjd0wk5tskkUUfuw4XxelcV6R9zWO3cN"


@inject
def main(
        sold_contracts_for_period_discord_renderer: SoldContractsForPeriodDiscordRenderer = Provide[
            ApplicationContainer.renderers.sold_contracts_for_period_discord_renderer
        ],
):
    webhook = Webhook.from_url(my_hook, adapter=RequestsWebhookAdapter())

    source: Observable = sold_contracts_for_period_discord_renderer.render()
    source.subscribe(lambda x: webhook.send(x), lambda e: logger.error(str(e), exc_info=True))


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
