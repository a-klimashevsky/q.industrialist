from eve.controllers import AssetsTreeController
from eve.domain import AssetsService
from eve.viewmodels import AssetTreeItemViewModel


class AssetsTreeControllerImpl(AssetsTreeController):

    _corp_assets_service: AssetsService

    def __init__(self,
                 corp_assets_service: AssetsService,
                 ):
        self._corp_assets_gateway = corp_assets_service
        pass

    def tree(self) -> AssetTreeItemViewModel:
        pass
