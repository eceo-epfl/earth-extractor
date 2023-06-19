from typing import Any, Dict, List
from earth_extractor.classes import Satellite
from earth_extractor.models import ROI
import logging
import datetime
logger = logging.getLogger(__name__)


class Provider:
    def __init__(
        self,
        name: str,
        satellites: Dict[Satellite, str],
        description: str | None = None,
        uri: str | None = None,
    ):
        self.name = name
        self.description = description
        self.uri = uri
        self.satellites = satellites

    def query(
        self,
        satellite: Satellite,
        roi: ROI,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: int = 100,
    ) -> List[Any]:
        ''' Query the provider for items matching the given parameters '''

        return []

    def download_items(
            self,
            items: List[Any],
    ) -> Any:

        pass
