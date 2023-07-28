from earth_extractor.providers import Provider
import logging
from earth_extractor.satellites import enums
from earth_extractor import core
from earth_extractor.core.credentials import get_credentials
from earth_extractor.core.models import CommonSearchResult
from typing import Any, List, TYPE_CHECKING
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
        cloud_cover: int | None = None,
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

        year = 2020
        headers = {
            "type": "Polygon",
            "crs": {"type": "name", "properties": {"name": "EPSG:2056"}},
            "coordinates": [
                [
                    [2618237.3216779926, 1205413.977215467],
                    [2650961.126517095, 1206868.3685416495],
                    [2656051.4961587335, 1179962.1290072764],
                    [2626236.4739719955, 1175598.9550287293],
                    [2618237.3216779926, 1205413.977215467],
                ]
            ],
        }

        # Convert datetime to unix time 1601942400000 represents 2020-10-06
        # two hours after midnight (Zurich time) representing an offset of 7200
        # seconds. Therefore an incoming date of 2020-10-06 will be converted
        # to 1601942400000. The unix timestamp here is also represented in
        # milliseconds, so we multiply by 1000.
        start_date_unix = int(
            (start_date + datetime.timedelta(hours=2)).timestamp() * 1000
        )
        end_date_unix = int(
            (end_date + datetime.timedelta(hours=2)).timestamp() * 1000
        )
        request_epsg = 2056
        # Get the resolution from the products dictionary based on CLI choice
        resolution = self.products.get((satellite.name, processing_level))[0]
        product = "ch.swisstopo.swissimage-dop10"

        # wgs84_box = box(
        #     7.234485381825444,
        #     46.16001032919722,
        #     7.450015649232836,
        #     46.28278844442293,
        # )

        wgs84 = pyproj.CRS("EPSG:4326")
        utm = pyproj.CRS("EPSG:2056")

        project = pyproj.Transformer.from_crs(
            wgs84, utm, always_xy=True
        ).transform
        roi_utm = transform(project, roi)

        utm_bounds_int = [int(x) for x in roi_utm.bounds]

        x_min, y_min, x_max, y_max = utm_bounds_int

        # Options seem to be 2017, 2018, 2019, 2020, 2021, 2022 and current
        # If set to None, it will return all years which is confusing because
        # we can also query for time period. Therefore we should write a
        # function that determines the years in the time period given by the
        # user and then query for those years... Or we can do a string filter
        # on the results to only return the years we want (easier and faster).
        year_collection = None

        # form_data="{'{\n++++++++"type":+"Polygon",\n++++++++"crs":+{"type":+"name",+"properties":+{"name":+"EPSG:2056"}},\n++++++++"coordinates":+[[[2618237.3216779926,1205413.977215467],[2650961.126517095,1206868.3685416495],[2656051.4961587335,1179962.1290072764],[2626236.4739719955,1175598.9550287293],[2618237.3216779926,1205413.977215467]]]\n++++++}'}"
        url = (
            "https://ogd.swisstopo.admin.ch/services/swiseld/services/assets/"
            f"{product}/search"
            "?format=image/tiff; application=geotiff; "
            f"profile=cloud-optimized&{resolution}&srid={request_epsg}"
            f"&state={year_collection if year_collection is not None else ''}"
            # f"&state={year_collection}"
            f"&from={start_date_unix}&to={end_date_unix}"
            # "&xMin=2588462&yMin=1117167&xMax=2596188&yMax=1123802&csv=true"
            f"&xMin={x_min}&yMin={y_min}&xMax={x_max}&yMax={y_max}&csv=true"
        )
        print(url)
        res = requests.get(url)
        # res = requests.get(
        #     # f"https://ogd.swisstopo.admin.ch/services/swiseld/services/assets/ch.swisstopo.swissimage-dop10/search?format=image/tiff; application=geotiff; profile=cloud-optimized&resolution=0.1&srid=2056&state={year}",
        #     "https://ogd.swisstopo.admin.ch/services/swiseld/services/assets/"
        #     f"{product}/search"
        #     "?format=image/tiff; application=geotiff; "
        #     f"profile=cloud-optimized&{resolution}&srid={request_epsg}"
        #     f"&state=current&from={start_date_unix}&to={end_date_unix}"
        #     f"&xMin={x_min}&yMin={y_min}&xMax={x_max}&yMax={y_max}&csv=true",
        #     # f"&xMin=2588462&yMin=1117167&xMax=2596188&yMax=1123802&csv=true",
        #     # data={"geometry": json.dumps(headers)}
        # )
        print(product)
        print(resolution)
        print(request_epsg)
        print(start_date_unix, end_date_unix)
        print(x_min, y_min, x_max, y_max)
        print(f"First response: {res.status_code}")
        csv_path = res.json()["href"]
        print(csv_path)

        # import csv
        res = requests.get(csv_path)
        print(res.status_code)
        csv_file = res.content
        # print(csv_file)
        # The "csv" is a headerless, single-column CSV that can be parsed into one line per file by splitting by newline char
        file_list = csv_file.decode("utf-8").split("\n")
        [print(x) for x in file_list]
        logger.info(f"{self.name}: Found {len(file_list)} files to download")
        # logger.info(f"NASA CMR: Found {len(features)} files to download")

        # return self.translate_search_results(features)
        records = self.translate_search_results(file_list, resolution)

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
        for result in search_results:
            file_path = result.url
            print(file_path)

            response = requests.get(file_path, stream=True)
            response.raise_for_status()
            # import os

            output_file_path = os.path.join(
                download_dir, file_path.split("/")[-1]
            )
            with open(output_file_path, "wb") as output_file:
                for chunk in response.iter_content(chunk_size=8192):
                    output_file.write(chunk)


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
