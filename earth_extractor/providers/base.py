from typing import Any, Dict, List, Tuple, TYPE_CHECKING
from earth_extractor import core
import logging
import datetime
import os

if TYPE_CHECKING:
    from earth_extractor.satellites import enums
    from earth_extractor.satellites.base import Satellite

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


class Provider:
    def __init__(
        self,
        name: str,
        satellites: Dict["enums.Satellite", str],
        description: str | None = None,
        uri: str | None = None,
        products: Dict[
            Tuple["enums.Satellite", "enums.ProcessingLevel"], Any
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
        roi: core.models.BBox,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: int = 100,
    ) -> List[Any]:
        ''' Query the provider for items matching the given parameters '''

        raise NotImplementedError(
            f"Query method not implemented for Provider: {self.name} "
            f"({self.description})"
        )

    def download_one(
        self,
        search_origin: "Provider",
        search_results: List[str],
        download_dir: str,
        processes: int = 6
    ) -> Any:

        raise NotImplementedError(
            f"Download method not implemented for Provider: {self.name} "
            f"({self.description})"
        )

    def download_many(
        self,
        search_origin: "Provider",
        search_results: List[str],
        download_dir: str,
        processes: int = 6
    ) -> Any:

        raise NotImplementedError(
            f"Download method not implemented for Provider: {self.name} "
            f"({self.description})"
        )

    def create_download_folder(
        self,
        folder_name: str,
    ) -> None:
        ''' Create a download folder if it doesn't exist '''

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

    def translate_search_results(
        self,
        provider_search_results: Dict[Any, Any]
    ) -> List[core.models.CommonSearchResult]:

        raise NotImplementedError(
            "Search translation method not implemented for Provider: "
            f"{self.name} ({self.description})"
        )
