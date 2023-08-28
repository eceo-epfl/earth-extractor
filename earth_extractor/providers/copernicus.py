from earth_extractor.providers import Provider
from earth_extractor.core.credentials import get_credentials
from earth_extractor.core.models import CommonSearchResult
from typing import Any, List, TYPE_CHECKING, Dict, Tuple, Optional
import sentinelsat
from earth_extractor.providers.extensions.sentinelsat import (
    SentinelAPIExtended,
)
import logging
import datetime
import shapely
import shapely.geometry
from earth_extractor.satellites import enums
from earth_extractor import core
import tenacity


if TYPE_CHECKING:
    from earth_extractor.satellites.base import Satellite

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

credentials = get_credentials()


class CopernicusOpenAccessHub(Provider):
    def query(
        self,
        satellite: "Satellite",
        processing_level: enums.ProcessingLevel,
        roi: shapely.geometry.base.BaseGeometry,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: Optional[int] = None,
    ) -> List[Dict[Any, Any]]:
        """Query the Copernicus Open Access Hub for data"""

        # Check that the provider's credentials that are needed are set
        self._check_credentials_exist()

        try:
            api = SentinelAPIExtended(
                credentials.SCIHUB_USERNAME, credentials.SCIHUB_PASSWORD
            )
        except sentinelsat.UnauthorizedError as e:
            logger.error(f"ASF authentication error: {e}")
            return []

        # If cloud cover percentage is 100, set to None for API
        if cloud_cover == 100:
            cloud_cover = None

        # Variable to combine all CommonSearchResult objects into one
        all_products = []

        for product_type in self.products.get(
            (satellite.name, processing_level), []
        ):
            # We do a list here because in some cases, a satellite may have
            # multiple product types for a given processing level (sentinel 3
            # has two product types for L2)
            logger.info(f"Product type: {product_type}")
            if not product_type:
                raise ValueError(
                    f"Processing level {processing_level.value} not supported "
                    f"by Copernicus Open Access Hub for satellite "
                    f"{satellite.name}. Available processing levels: "
                    f"{self.products}"
                )

            try:
                products = api.query(
                    roi.wkt,
                    producttype=product_type,
                    cloudcoverpercentage=(0, cloud_cover)
                    if cloud_cover
                    else None,
                    date=(start_date, end_date),
                )
                # Translate the results to a common format
                products = self.translate_search_results(products)

                all_products += products
            except sentinelsat.UnauthorizedError as e:
                logger.error(f"SentinelSat authentication error: {e}")
                return []

        return all_products

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(
            sentinelsat.exceptions.ServerError
        ),
        stop=tenacity.stop_after_attempt(
            core.config.constants.MAX_DOWNLOAD_ATTEMPTS
        ),
        wait=tenacity.wait_fixed(90),  # API rate limit is 90req/60s
        reraise=True,
    )
    def download_many(
        self,
        search_results: List[CommonSearchResult],
        download_dir: str,
        overwrite: bool = False,
        processes: int = core.config.constants.PARRALLEL_PROCESSES_DEFAULT,
        *,
        max_attempts: int = core.config.constants.MAX_DOWNLOAD_ATTEMPTS,
    ) -> None:
        """Using the search results from query(), download the data

        Function will retry if the API returns a 500 error. This can happen
        when the API is under heavy load or when the API rate limit is exceeded
        which is defined at time of writing to be 90 requests per minute.

        Parameters
        ----------
        search_results : List[str]
            The search results
        download_dir : str
            The directory to download the data to
        overwrite : bool
            Whether to overwrite existing files
        processes : int
            The number of processes to use for downloading

        Returns
        -------
        None
        """
        # Check that the provider's credentials that are needed are set
        self._check_credentials_exist()

        logger.addHandler(sentinelsat.SentinelAPI.logger)

        # Convert the search results to a list of product ids
        product_ids = [result.product_id for result in search_results]

        api = SentinelAPIExtended(
            credentials.SCIHUB_USERNAME, credentials.SCIHUB_PASSWORD
        )
        api.download_all(
            product_ids,
            directory_path=download_dir,
            n_concurrent_dl=processes,
            checksum=True,
            max_attempts=max_attempts,
            overwrite=overwrite,
        )

    def translate_search_results(
        self, provider_search_results: Dict[Any, Any]
    ) -> List[CommonSearchResult]:
        """Translate search results from a provider to a common format

        Parameters
        ----------
        provider_search_results : Dict[Any, Any]
            The search results from the provider

            Returns
            -------
            List[CommonSearchResult]
                The search results in a common format
        """

        common_results = []
        for id, props in provider_search_results.items():
            # Get the satellite and processing level from reversed mapping of
            # the provider's "products" dictionary
            sat, level = self._products_reversed[props["producttype"]]

            common_results.append(
                CommonSearchResult(
                    geometry=props.get("footprint"),
                    product_id=id,
                    link=props.get("link_alternative"),
                    identifier=props.get("identifier"),
                    filename=props.get("filename"),
                    size=props.get("size"),
                    time=props.get("beginposition"),
                    cloud_cover_percentage=props.get("cloudcoverpercentage"),
                    processing_level=level,
                    satellite=sat,
                )
            )

        return common_results


copernicus_scihub: CopernicusOpenAccessHub = CopernicusOpenAccessHub(
    name="scihub",
    description="Copernicus Open Access Hub",
    uri="https://scihub.copernicus.eu",
    products={
        (enums.Satellite.SENTINEL1, enums.ProcessingLevel.L1): ["GRD"],
        (enums.Satellite.SENTINEL2, enums.ProcessingLevel.L1C): ["S2MSI1C"],
        (enums.Satellite.SENTINEL2, enums.ProcessingLevel.L2A): ["S2MSI2A"],
        (enums.Satellite.SENTINEL3, enums.ProcessingLevel.L1): ["OL_1_EFR___"],
        (enums.Satellite.SENTINEL3, enums.ProcessingLevel.L2): [
            "OL_2_LFR___",
            "OL_2_WFR___",
        ],
    },
    credentials_required=["SCIHUB_USERNAME", "SCIHUB_PASSWORD"],
)
