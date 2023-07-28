import tenacity
from earth_extractor.providers import Provider
import logging
from earth_extractor.satellites import enums
from earth_extractor import core
from earth_extractor.core.credentials import get_credentials
from earth_extractor.core.models import CommonSearchResult
from typing import Any, List, TYPE_CHECKING, Optional
import pyproj
from shapely.geometry import box
from shapely.ops import transform
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
        """Perform a search query as if done via SwissTopo web interface

        Method discovery by inspecting the network traffic of the SwissTopo
        web interface.
        https://www.swisstopo.admin.ch/en/geodata/images/ortho/swissimage10.html#download  # noqa: E501

        Local ROI is WGS84, EPSG:4326, but SwissTopo API requires CH1903+
        coordinates. We must cast the ROI to CH1903+ EPSG: 2056 before querying
        the API even though there appears to be a CRS parameter in the
        API -- as API is undocumented, it's best to play it safe.
        """

        logger.info(f"{self.name}: Querying API")

        # Convert datetime to unix time 1601942400000 represents 2020-10-06
        # two hours after midnight (Zurich time) representing an offset of 7200
        # seconds. Therefore an incoming date of 2020-10-06 will be converted
        # to 1601942400000. The unix timestamp here is also represented in
        # milliseconds, so we multiply by 1000.
        start_date_unix = int(
            (start_date + datetime.timedelta(hours=2)).timestamp() * 1000
        )

        # I have a suspicion that start time is offset by +2 hours, to
        # Europe/Zurich but the end_time is still UTC +0 hours. There is no
        # adjustment here for this, but it may be worth investigating in the
        # future.
        end_date_unix = int(
            (end_date + datetime.timedelta(hours=2)).timestamp() * 1000
        )
        request_epsg = 2056

        # Get the resolution from the products dictionary based on CLI choice
        # Normally this would be a satellite processing level, but in this case
        # it's a resolution. Rather than redesigning the code for this one use
        # case (SwissTopo), we can just use the resolution as the processing
        # level. May be worth changing in the future
        resolution = self.products[(satellite.name, processing_level)][0]
        product = "ch.swisstopo.swissimage-dop10"

        # Reproject coordinates from WGS84 to CH1903+ (EPSG:2056)
        wgs84 = pyproj.CRS("EPSG:4326")
        utm = pyproj.CRS("EPSG:2056")

        project = pyproj.Transformer.from_crs(
            wgs84, utm, always_xy=True
        ).transform
        roi_utm = transform(project, roi)
        x_min, y_min, x_max, y_max = roi_utm.bounds

        # Options seem to be 2017, 2018, 2019, 2020, 2021, 2022 and "current".
        # If set to None, it will return all years which is confusing because
        # we can also query for time period. We can do a string filter
        # on the results to only return the years we want (faster queries but
        # a bit hacky). Ensure the assumptions are tested at runtime.
        year_collection = None

        url = (
            "https://ogd.swisstopo.admin.ch/services/swiseld/services/assets/"
            f"{product}/search"
            "?format=image/tiff; application=geotiff; "
            f"profile=cloud-optimized&{resolution}&srid={request_epsg}"
            f"&state={year_collection if year_collection is not None else ''}"
            f"&from={start_date_unix}&to={end_date_unix}"
            f"&xMin={x_min}&yMin={y_min}&xMax={x_max}&yMax={y_max}&csv=true"
        )

        res = requests.get(url)
        res.raise_for_status()

        logger.debug(f"Unix time: {start_date_unix}, {end_date_unix}")
        logger.debug(f"Bounds {x_min}, {y_min}, {x_max}, {y_max}")

        # Get the CSV path from JSON response
        csv_path = res.json()["href"]
        logger.debug(f"CSV Path: {csv_path}")

        # import csv
        res = requests.get(csv_path)
        res.raise_for_status()

        # The "csv" is a headerless, single-column CSV that can be parsed into
        # one line per file by splitting by newline char
        file_list = res.content.decode("utf-8").split("\n")

        # We can try and make an assumption that the returned addresses stated:
        # https://<url>/swissimage-dop10_<i>_<j>-<k>/filename.tif can relate to
        # the following:
        # i = year
        # j = unknown (flight #?)
        # k = unknown (tile #?)
        # We can then filter the results based on the year we want to download
        # and then download the files.

        filtered_file_list = []
        for url_path in file_list:
            subpath, _filename = url_path.split("/")[-2:]

            # Split the subpath into its components (as listed above)
            subpath_split = subpath.split("_")
            if (
                subpath_split[0] == "swissimage-dop10"
                and len(str(subpath_split[1])) == 4
            ):
                # Get the range of years given by the user in a sequential list
                # and then filter the results based on that list
                year_range = list(range(start_date.year, end_date.year + 1))
                if int(subpath_split[1]) in year_range:
                    filtered_file_list.append(url_path)
            else:
                raise ValueError(
                    f"Unexpected file path provided by SwissTopo: '{url_path}'"
                    " This breaks the assumption of yearly filtering. Please "
                    "report this issue to the developers."
                )
        [logger.debug(f"{self.name}: {x}") for x in filtered_file_list]

        logger.info(
            f"{self.name}: Found {len(filtered_file_list)} files to download"
        )

        records = self.translate_search_results(filtered_file_list, resolution)

        return records

    def translate_search_results(
        self,
        provider_search_results: Any,
        resolution: str,
    ) -> List[CommonSearchResult]:
        """Translate search results from a provider to a common format"""

        sat, level = self._products_reversed[resolution]

        common_results = []
        for item in provider_search_results:
            # Swiss Topo does not provide any geometry information

            common_results.append(
                CommonSearchResult(
                    url=item,
                    satellite=sat,
                )
            )

        return common_results

    def download_many(
        self,
        search_results: List[CommonSearchResult],
        download_dir: str,
        processes: int = core.config.constants.PARRALLEL_PROCESSES_DEFAULT,
        *,
        max_attempts: int = core.config.constants.MAX_DOWNLOAD_ATTEMPTS,
    ) -> None:
        """Download many files from the SwissTopo API

        Uses the common download utility with progress bar
        """

        search_results = [str(x.url) for x in search_results]
        core.utils.download_parallel(search_results, download_dir)


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
