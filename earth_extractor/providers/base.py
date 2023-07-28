from typing import Any, Dict, List, Tuple, TYPE_CHECKING, Optional
from earth_extractor import core
import logging
import datetime
import os
import shapely.geometry
from earth_extractor.core.models import CommonSearchResult
from pystac_client import Client

if TYPE_CHECKING:
    from earth_extractor.satellites import enums
    from earth_extractor.satellites.base import Satellite

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


class Provider:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        uri: Optional[str] = None,
        products: Dict[
            Tuple["enums.Satellite", "enums.ProcessingLevel"], List[Any]
        ] = {},
    ):
        """A provider of satellite data

        Parameters
        ----------
        name : str
            The name of the provider
        description : str, optional
            A description of the provider, by default None
        uri : str, optional
            A URI for the provider, by default None
        products : Dict[Tuple[Satellite, ProcessingLevel], List[Any]], optional
            A dictionary of the products supported by the provider. The key
            is a tuple of the satellite enum and the processing level enum.
            The value is a list of the products supported by the provider and
            in most cases is a single item, however, some providers may provide
            multiple products for a given satellite and processing level. For
            the sake of simplicity, the only case that does this at the time
            of this writing is the Copernicus Open Access Hub, which provides
            LFR and WFR products for Sentinel3 L2 data.
            )
            For example:
            {
                (enums.Satellite.SENTINEL1, enums.ProcessingLevel.GRD):
                    ["IW", "EW"]
            }
            by default {}

        Raises
        ------
        NotImplementedError
            If the query method is not implemented
        """
        self.name = name
        self.description = description
        self.uri = uri
        self.products = products

    def query(
        self,
        satellite: "Satellite",
        processing_level: "enums.ProcessingLevel",
        roi: core.models.BBox,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: int = 100,
    ) -> List[CommonSearchResult]:
        """Query the provider for items matching the given parameters"""

        raise NotImplementedError(
            f"Query method not implemented for Provider: {self.name} "
            f"({self.description})"
        )

    def download_many(
        self,
        search_results: List[CommonSearchResult],
        download_dir: str,
        processes: int = 6,
    ) -> Any:
        raise NotImplementedError(
            f"Download method not implemented for Provider: {self.name} "
            f"({self.description})"
        )

    def create_download_folder(
        self,
        folder_name: str,
    ) -> None:
        """Create a download folder if it doesn't exist"""

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

    def translate_search_results(
        self,
        *,
        provider_search_results: Dict[Any, Any],
    ) -> List[core.models.CommonSearchResult]:
        raise NotImplementedError(
            "Search translation method not implemented for Provider: "
            f"{self.name} ({self.description})"
        )

    @property
    def _products_reversed(
        self,
    ) -> Dict[Any, Tuple["enums.Satellite", "enums.ProcessingLevel"]]:
        """A reverse of the property dictionary

        Makes sure that each item in the list each value is now its own key
        and the original key is now a value in the list

        For example, a dictionary of the form:
        {
            ("Sentinel-1", "GRD"): ["IW", "EW"]
        }
        Will become a dictionary of the form:
        {
            "IW": ("Sentinel-1", "GRD"),
            "EW": ("Sentinel-1", "GRD")
        }
        """

        products_reversed = {}
        for key, value in self.products.items():
            for item in value:
                products_reversed[item] = key

        return products_reversed

    def query_stac(
        self,
        provider_uri: str,
        collections: List[str],
        roi: shapely.geometry.base.BaseGeometry,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> Dict[str, str]:
        """A generic STAC query method for providers that support STAC

        Parameters
        ----------
        provider_uri : str
            The URI of the provider
        collections : List[str]
            A list of collections to query
        roi : shapely.geometry.base.BaseGeometry
            The region of interest
        start_time : datetime.datetime
            The start time of the query
        end_time : datetime.datetime
            The end time of the query

        Returns
        -------
        Dict[str, str]
            A dictionary of the results
        """

        catalog = Client.open(provider_uri)

        logger.info(f"Querying STAC URI: {provider_uri}")
        search = catalog.search(
            collections=collections,
            intersects=roi,
            datetime=[start_date.isoformat(), end_date.isoformat()],
        )

        return search.item_collection_as_dict()
