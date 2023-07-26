from earth_extractor.providers import Provider
import logging
from earth_extractor.satellites import enums
from earth_extractor import core
from earth_extractor.core.credentials import get_credentials
from earth_extractor.core.models import CommonSearchResult
from typing import Any, List, TYPE_CHECKING
from pydantic import AnyUrl
import os
import datetime
import tqdm
import shapely.geometry
from shapely.geometry import Polygon
from pystac_client import Client
import requests


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
        cloud_cover: int | None = None,
    ) -> List[CommonSearchResult]:
        """Query the Copernicus Open Access Hub for data"""

        catalog = Client.open(f"{self.uri}/stac/LAADS")

        logger.info("Querying NASA Common Metadata Repository")
        search = catalog.search(
            collections=self.products[(satellite.name, processing_level)],
            intersects=roi,
            datetime=[start_date.isoformat(), end_date.isoformat()],
        )
        records = search.item_collection_as_dict()["features"]
        logger.info(f"NASA CMR: Found {len(records)} files to download")

        return self.translate_search_results(records)

    def translate_search_results(
        self, provider_search_results: Any
    ) -> List[CommonSearchResult]:
        """Translate search results from a provider to a common format"""

        common_results = []
        for record in provider_search_results:
            # Get the satellite and processing level from reversed mapping of
            # the provider's "products" dictionary
            sat, level = self._products_reversed[record["collection"]]

            common_results.append(
                CommonSearchResult(
                    product_id=record["id"],
                    time=record["properties"]["datetime"],
                    geometry=Polygon(record["geometry"]["coordinates"][0]),
                    url=record["assets"]["data"]["href"],
                    processing_level=level,
                    satellite=sat,
                )
            )

        return common_results

    # @tenacity.retry(
    #     retry=tenacity.retry_if_exception_type(
    #         sentinelsat.exceptions.ServerError
    #     ),
    #     stop=tenacity.stop_after_attempt(
    #         core.config.constants.MAX_DOWNLOAD_ATTEMPTS
    #     ),
    #     wait=tenacity.wait_fixed(90),  # API rate limit is 90req/60s
    #     reraise=True
    # )
    def download_many(
        self,
        search_results: List[CommonSearchResult],
        download_dir: str,
        processes: int = core.config.constants.PARRALLEL_PROCESSES_DEFAULT,
        *,
        max_attempts: int = core.config.constants.MAX_DOWNLOAD_ATTEMPTS,
    ) -> None:
        """Using the search results from query(), download the data

        Parameters
        ----------
        search_results : List[str]
            The search results
        download_dir : str
            The directory to download the data to
        processes : int
            The number of processes to use for downloading

        Returns
        -------
        None
        """

        # Convert the search results to a list of URIs
        urls: list[AnyUrl] = [x.url for x in search_results if x.url]

        auth_header = {"Authorization": f"Bearer {credentials.NASA_TOKEN}"}
        # Get total size
        # total = 0
        # for url in urls:

        for url in urls:
            # url_header = requests.head(url, headers=auth_header).raw.headers
            # total_size = int(url_header.get('content-length', -1))
            # logger.info(f"Total size: {total_size}")

            resp = requests.get(url, stream=True, headers=auth_header).raw

            if resp.status == 200:
                try:
                    output_path = os.path.join(
                        download_dir,
                        url.split("/")[-1],
                    )
                    with open(output_path, "wb") as dest:
                        with tqdm.tqdm(
                            desc=url,
                            unit="iB",
                            unit_scale=True,
                            unit_divisor=1024,
                        ) as bar:
                            while True:
                                data = resp.read(4096)
                                if not data:
                                    break
                                size = dest.write(data)
                                bar.update(size)
                finally:
                    resp.release_conn()
            else:
                total_size = 0
        # requests.get()
        # api = sentinelsat.SentinelAPI(
        #     credentials.SCIHUB_USERNAME,
        #     credentials.SCIHUB_PASSWORD
        # )

        # api.download_all(
        #     search_results,
        #     directory_path=download_dir,
        #     n_concurrent_dl=processes,
        #     checksum=True,
        #     max_attempts=max_attempts,
        # )

    # def sign_urls(
    #     self,
    #     urls: List[str],
    #     authentication_uri: str = "urs.earthdata.nasa.gov",
    # ) -> str:
    #     ''' Sign the URLs for download with NASA Earthdata authentication '''

    #     for url in urls:

    #     username, account, password = netrc.netrc().authenticators(
    #         authentication_uri
    #     )
    #     # fsspec.config.conf['https'] = dict(
    #     creds = dict(
    #         client_kwargs={'auth':
    #             aiohttp.BasicAuth(
    #                 credentials.NASA_USERNAME,
    #                 credentials.NASA_PASSWORD
    #             )
    #         }
    #     )
    #     print(creds)
    #     # return username, password

    #     return url


nasa_cmr: NASACommonMetadataRepository = NASACommonMetadataRepository(
    name="CMR",
    description="NASA Common Metadata Repository",
    satellites={
        enums.Satellite.MODIS_TERRA: "",
        enums.Satellite.MODIS_AQUA: "",
    },  # Redundant?
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
    },
    uri="https://cmr.earthdata.nasa.gov",
)
