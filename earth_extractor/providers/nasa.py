from earth_extractor.providers import Provider
import logging
from earth_extractor.satellites import enums
from earth_extractor import core
from earth_extractor.core.credentials import get_credentials
from earth_extractor.core.models import CommonSearchResult
from typing import Any, List, TYPE_CHECKING, Optional
import datetime
import shapely.geometry
from shapely.geometry import Polygon


if TYPE_CHECKING:
    from earth_extractor.satellites.base import Satellite

credentials = get_credentials()

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


class NASACommonMetadataRepository(Provider):
    def query(
        self,
        satellite: "Satellite",
        processing_level: enums.ProcessingLevel,
        roi: shapely.geometry.base.BaseGeometry,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: Optional[int] = None,
    ) -> List[CommonSearchResult]:
        """Query the NASA Common Metadata Repository with STAC"""

        # Check that the provider's credentials that are needed are set
        self._check_credentials_exist()

        logger.info("Querying NASA Common Metadata Repository")
        res = self.query_stac(
            provider_uri=f"{self.uri}/stac/LAADS",
            collections=self.products[(satellite.name, processing_level)],
            roi=roi,
            start_date=start_date,
            end_date=end_date,
        )
        features = res["features"]

        logger.info(f"NASA CMR: Found {len(features)} files to download")

        return self.translate_search_results(features)

    def translate_search_results(
        self, provider_search_results: Any
    ) -> List[CommonSearchResult]:
        """Translate search results from a provider to a common format"""

        common_results = []
        for record in provider_search_results:
            # Get the satellite and processing level from reversed mapping of
            # the provider's "products" dictionary
            sat, level = self._products_reversed[record["collection"]]
            datetime_obj = datetime.datetime.strptime(
                record["properties"]["datetime"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )

            common_results.append(
                CommonSearchResult(
                    product_id=record["id"],
                    time=datetime_obj,
                    geometry=Polygon(record["geometry"]["coordinates"][0]),
                    url=record["assets"]["data"]["href"],
                    processing_level=level,
                    satellite=sat,
                )
            )

        return common_results

    def download_many(
        self,
        search_results: List[CommonSearchResult],
        download_dir: str,
        overwrite: bool = False,
        processes: int = core.config.constants.PARRALLEL_PROCESSES_DEFAULT,
    ) -> None:
        """Using the search results from query(), download the data

        Parameters
        ----------
        search_results : List[str]
            The search results
        download_dir : str
            The directory to download the data to
        overwrite : bool, optional
            Whether to overwrite existing files, by default False
        processes : int, optional
            The number of processes to use for downloading

        Returns
        -------
        None
        """

        # Convert the search results to a list of URIs

        # Check that the provider's credentials that are needed are set
        self._check_credentials_exist()

        urls = [str(x.url) for x in search_results if x.url]

        auth_header = {"Authorization": f"Bearer {credentials.NASA_TOKEN}"}

        for url in urls:
            try:
                core.utils.download_parallel(
                    urls, download_dir, auth_header, overwrite, processes
                )
            except RuntimeError as e:
                # Log the exception and continue to the next file
                logger.error(e)
                continue


nasa_cmr: NASACommonMetadataRepository = NASACommonMetadataRepository(
    name="CMR",
    description="NASA Common Metadata Repository",
    products={
        (enums.Satellite.MODIS_TERRA, enums.ProcessingLevel.L1B): [
            "MOD02QKM.v6.1",
            "MOD02HKM.v6.1",
            "MOD021KM.v6.1",
            "MOD03.v6.1",
        ],
        (enums.Satellite.MODIS_AQUA, enums.ProcessingLevel.L1B): [
            "MYD02QKM.v6.1",
            "MYD02HKM.v6.1",
            "MYD021KM.v6.1",
            "MYD03.v6.1",
        ],
        (enums.Satellite.VIIRS, enums.ProcessingLevel.L1): [
            "VNP03IMG.v2",
            "VJ103IMG.v2.1",
            "VNP03MOD.v2",
            "VJ103MOD.v2.1",
        ],
    },
    uri="https://cmr.earthdata.nasa.gov",
    credentials_required=["NASA_TOKEN"],
)
