from typing import Any, Dict, List, Tuple, TYPE_CHECKING
from earth_extractor.models import ROI
import logging
import datetime
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from earth_extractor.satellites import enums
    from earth_extractor.satellites.base import Satellite


class Provider:
    def __init__(
        self,
        name: str,
        satellites: Dict["enums.Satellite", str],
        # processing_levels: Dict["enums.ProcessingLevel", str],
        description: str | None = None,
        uri: str | None = None,
        products: Dict[
            Tuple["enums.Satellite", "enums.ProcessingLevel"], str
        ] = {},
    ):
        self.name = name
        self.description = description
        self.uri = uri
        self.satellites = satellites
        self.products = products

    def query(
        self,
        satellite: "Satellite",
        processing_level: "enums.ProcessingLevel",
        roi: ROI,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: int = 100,
    ) -> List[Any]:
        ''' Query the provider for items matching the given parameters '''

        return []

    def download_one(
            self,
            items: List[Any],
    ) -> Any:

        pass

    def download_many(
            self,
            items: List[Any],
    ) -> Any:

        pass
