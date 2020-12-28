import sys
from typing import List, Dict

import requests

from app.domain import Asset
from app.domain.get_foreign_structures_ids import get_foreign_structures_ids
from app.esi import StructureData
from app.domain.gateways import ForeignStructuresGateway
from eve_esi_interface import EveOnlineInterface


class ForeignStructuresGatewayImpl(ForeignStructuresGateway):
    _eve_interface: EveOnlineInterface

    _cache = None

    def __init__(self, eve_interface: EveOnlineInterface):
        self._eve_interface = eve_interface
        pass

    def structures(self, corp_assets_data: List[Asset]) -> Dict[str, StructureData]:
        if self._cache is None:
            self._cache = self._structures(corp_assets_data)
        return self._cache

    def _structures(self, corp_assets_data: List[Asset]) -> Dict[str, StructureData]:
        foreign_structures_data: Dict[str, StructureData] = {}
        foreign_structures_ids = get_foreign_structures_ids(corp_assets_data)
        foreign_structures_forbidden_ids = []
        if len(foreign_structures_ids) > 0:
            # Requires: access token
            for structure_id in foreign_structures_ids:
                try:
                    universe_structure_data = self._eve_interface.get_esi_data(
                        "universe/structures/{}/".format(structure_id),
                        fully_trust_cache=True)
                    foreign_structures_data.update(
                        {str(structure_id): StructureData.from_dict(universe_structure_data)})
                except requests.exceptions.HTTPError as err:
                    status_code = err.response.status_code
                    if status_code == 403:  # это нормально, что часть структур со временем могут оказаться Forbidden
                        foreign_structures_forbidden_ids.append(structure_id)
                    else:
                        raise
                except:
                    print(sys.exc_info())
                    raise

        sys.stdout.flush()
        return foreign_structures_data