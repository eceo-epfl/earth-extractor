from earth_extractor.providers import Provider
import logging
from earth_extractor.satellites import enums
from earth_extractor import core
from earth_extractor.core.credentials import get_credentials
from earth_extractor.core.models import CommonSearchResult
from typing import Any, List, TYPE_CHECKING, Optional
import datetime
import shapely.geometry


if TYPE_CHECKING:
    from earth_extractor.satellites.base import Satellite

credentials = get_credentials()

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

STAC_API_URL = "https://data.geo.admin.ch/api/stac/v1/"
COLLECTION = "ch.swisstopo.swissimage-dop10"


class SwissTopo(Provider):
    def query(
        self,
        satellite: "Satellite",
        processing_level: enums.ProcessingLevel,
        roi: shapely.geometry.base.BaseGeometry,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: Optional[int] = None,
    ) -> List[CommonSearchResult]:
        """Query the SwissTopo STAC API for SWISSIMAGE tiles

        Uses the official STAC API at data.geo.admin.ch to search for
        SWISSIMAGE 10cm orthophotos within the given ROI and date range.
        """

        logger.info(f"{self.name}: Querying STAC API")

        # Get the resolution from the products dictionary based on CLI choice
        # Normally this would be a satellite processing level, but in this case
        # it's a resolution. Rather than redesigning the code for this one use
        # case (SwissTopo), we can just use the resolution as the processing
        # level. May be worth changing in the future
        resolution = self.products[(satellite.name, processing_level)][0]

        # Extract the numeric resolution value (e.g., "0.1" from
        # "resolution=0.1") for filtering STAC asset filenames
        resolution_value = resolution.split("=")[1]

        # Use the base class query_stac method which handles pystac-client
        # queries. The STAC API accepts WGS84 bbox directly, so no
        # reprojection is needed.
        results = self.query_stac(
            provider_uri=STAC_API_URL,
            collections=[COLLECTION],
            roi=roi,
            start_date=start_date,
            end_date=end_date,
        )

        features = results.get("features", [])
        logger.info(
            f"{self.name}: STAC returned {len(features)} items"
        )

        records = self.translate_search_results(
            provider_search_results=features,
            resolution=resolution,
            resolution_value=resolution_value,
        )

        logger.info(
            f"{self.name}: Found {len(records)} files to download"
        )

        return records

    def translate_search_results(
        self,
        *,
        provider_search_results: Any,
        resolution: str,
        resolution_value: str,
    ) -> List[CommonSearchResult]:
        """Translate STAC search results to CommonSearchResult format

        Each STAC item may contain multiple assets. We filter assets by
        resolution using the filename pattern, e.g. filenames containing
        '_0.1_' for 10cm resolution or '_2.0_' for 2m resolution.

        Parameters
        ----------
        provider_search_results : list
            List of STAC item feature dicts from the STAC API response
        resolution : str
            The resolution string (e.g., "resolution=0.1") used to look up
            the satellite and processing level via _products_reversed
        resolution_value : str
            The numeric resolution value (e.g., "0.1") used to filter
            asset filenames
        """

        sat, level = self._products_reversed[resolution]

        common_results = []
        for item in provider_search_results:
            # Get the item geometry as WKT
            geom = shapely.geometry.shape(item["geometry"])
            geom_wkt = geom.wkt

            # Parse the item datetime for the time field
            item_datetime = None
            dt_str = item.get("properties", {}).get("datetime")
            if dt_str:
                item_datetime = datetime.datetime.fromisoformat(
                    dt_str.replace("Z", "+00:00")
                )

            # Filter assets by resolution in the filename
            # Asset keys use varying precision: '_0.1_' for 10cm, '_2_' for 2m
            # Normalize by also checking without trailing zeros
            res_normalized = resolution_value.rstrip("0").rstrip(".")
            assets = item.get("assets", {})
            for asset_key, asset_value in assets.items():
                href = asset_value.get("href", "")

                if (
                    f"_{resolution_value}_" in asset_key
                    or f"_{res_normalized}_" in asset_key
                ):
                    common_results.append(
                        CommonSearchResult(
                            url=href,
                            satellite=sat,
                            geometry=geom_wkt,
                            processing_level=level,
                            time=item_datetime,
                            identifier=item.get("id"),
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
        """Download many files from the SwissTopo API

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

        Uses the common download utility with progress bar.
        """

        urls = [str(x.url) for x in search_results]
        core.utils.download_parallel(
            urls, download_dir, overwrite=overwrite, processes=processes
        )


swiss_topo: SwissTopo = SwissTopo(
    name="SwissTopo",
    description="Swiss Federal Office of Topography",
    products={
        (enums.Satellite.SWISSIMAGE, enums.ProcessingLevel.CM10): [
            "resolution=0.1"
        ],
        (enums.Satellite.SWISSIMAGE, enums.ProcessingLevel.CM200): [
            "resolution=2.0"
        ],
    },
    uri="https://data.geo.admin.ch",
)
