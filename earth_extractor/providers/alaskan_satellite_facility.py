from earth_extractor.providers import Provider
import logging
from typing import List
import asf_search
from earth_extractor.core.credentials import get_credentials
from earth_extractor import core


###

from typing import Iterable
from multiprocessing import Pool
import os.path
import urllib.parse
from requests import Response
from requests.exceptions import HTTPError
import warnings
import regex as re
from asf_search.download.download import _try_get_response
from asf_search.exceptions import ASFAuthenticationError, ASFDownloadError
from asf_search import ASFSession
from remotezip import RemoteZip
from tenacity import retry, stop_after_delay, retry_if_result, wait_fixed
import sys
import logging
from typing import Generator, Union, Iterable, Tuple
from copy import copy
from requests.exceptions import HTTPError
from requests import ReadTimeout, Response
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_fixed,
)
import datetime
import dateparser
import warnings

from asf_search import __version__

from asf_search.ASFSearchResults import ASFSearchResults
from asf_search.ASFSearchOptions import ASFSearchOptions
from asf_search.CMR import build_subqueries, translate_opts
from asf_search.ASFSession import ASFSession
from asf_search.ASFProduct import ASFProduct
from asf_search.exceptions import (
    ASFSearch4xxError,
    ASFSearch5xxError,
    ASFSearchError,
    CMRIncompleteError,
)
from asf_search.constants import INTERNAL
from asf_search.WKT.validate_wkt import validate_wkt
from asf_search.search.error_reporting import report_search_error

###
logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

credentials = get_credentials()


def download_url(
    url: str, path: str, filename: str = None, session: ASFSession = None
) -> None:
    """
    Downloads a product from the specified URL to the specified location and (optional) filename.

    :param url: URL from which to download
    :param path: Local path in which to save the product
    :param filename: Optional filename to be used, extracted from the URL by default
    :param session: The session to use, in most cases should be authenticated beforehand
    :return:
    """
    sys.exit("TEST!!!")
    if filename is None:
        filename = os.path.split(urllib.parse.urlparse(url).path)[1]

    if not os.path.isdir(path):
        raise ASFDownloadError(
            f"Error downloading {url}: directory not found: {path}"
        )

    if os.path.isfile(os.path.join(path, filename)):
        warnings.warn(
            f"File already exists, skipping download: {os.path.join(path, filename)}"
        )
        return

    if session is None:
        session = ASFSession()

    response = _try_get_response(session=session, url=url)

    with open(os.path.join(path, filename), "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


from typing import Iterable
from copy import copy

# from asf_search.search import search
from asf_search.ASFSearchOptions import ASFSearchOptions
from asf_search.ASFSearchResults import ASFSearchResults

from asf_search import ASFProduct
from asf_search.search.search_generator import (
    preprocess_opts,
    get_page,
    process_page,
)
from asf_search.download.file_download_type import FileDownloadType

from typing import Iterable
from copy import copy

# from asf_search.search import search
from asf_search.ASFSearchOptions import ASFSearchOptions
from asf_search.ASFSearchResults import ASFSearchResults


class ASFProductExtended(ASFProduct):
    # Extend the class to override the download function
    def download(
        self,
        path: str,
        filename: str = None,
        session: ASFSession = None,
        fileType=FileDownloadType.DEFAULT_FILE,
    ) -> None:
        """
        Downloads this product to the specified path and optional filename.

        :param path: The directory into which this product should be downloaded.
        :param filename: Optional filename to use instead of the original filename of this product.
        :param session: The session to use, defaults to the one used to find the results.

        :return: None
        """

        default_filename = self.properties["fileName"]

        if filename is not None:
            multiple_files = (
                fileType == FileDownloadType.ADDITIONAL_FILES
                and len(self.properties["additionalUrls"]) > 1
            ) or fileType == FileDownloadType.ALL_FILES
            if multiple_files:
                warnings.warn(
                    f'Attempting to download multiple files for product, ignoring user provided filename argument "{filename}", using default.'
                )
            else:
                default_filename = filename

        if session is None:
            session = self.session

        urls = []

        def get_additional_urls():
            output = []
            base_filename = ".".join(default_filename.split(".")[:-1])
            for url in self.properties["additionalUrls"]:
                extension = url.split(".")[-1]
                urls.append((f"{base_filename}.{extension}", url))

            return output

        if fileType == FileDownloadType.DEFAULT_FILE:
            urls.append((default_filename, self.properties["url"]))
        elif fileType == FileDownloadType.ADDITIONAL_FILES:
            urls.extend(get_additional_urls())
        elif fileType == FileDownloadType.ALL_FILES:
            urls.append((default_filename, self.properties["url"]))
            urls.extend(get_additional_urls())
        else:
            raise ValueError(
                "Invalid FileDownloadType provided, the valid types are 'DEFAULT_FILE', 'ADDITIONAL_FILES', and 'ALL_FILES'"
            )

        for filename, url in urls:
            download_url(
                url=url, path=path, filename=filename, session=session
            )


def search_generator(
    absoluteOrbit: Union[
        int, Tuple[int, int], Iterable[Union[int, Tuple[int, int]]]
    ] = None,
    asfFrame: Union[
        int, Tuple[int, int], Iterable[Union[int, Tuple[int, int]]]
    ] = None,
    beamMode: Union[str, Iterable[str]] = None,
    beamSwath: Union[str, Iterable[str]] = None,
    campaign: Union[str, Iterable[str]] = None,
    maxDoppler: float = None,
    minDoppler: float = None,
    end: Union[datetime.datetime, str] = None,
    maxFaradayRotation: float = None,
    minFaradayRotation: float = None,
    flightDirection: str = None,
    flightLine: str = None,
    frame: Union[
        int, Tuple[int, int], Iterable[Union[int, Tuple[int, int]]]
    ] = None,
    granule_list: Union[str, Iterable[str]] = None,
    groupID: Union[str, Iterable[str]] = None,
    insarStackId: str = None,
    instrument: Union[str, Iterable[str]] = None,
    intersectsWith: str = None,
    lookDirection: Union[str, Iterable[str]] = None,
    offNadirAngle: Union[
        float, Tuple[float, float], Iterable[Union[float, Tuple[float, float]]]
    ] = None,
    platform: Union[str, Iterable[str]] = None,
    polarization: Union[str, Iterable[str]] = None,
    processingDate: Union[datetime.datetime, str] = None,
    processingLevel: Union[str, Iterable[str]] = None,
    product_list: Union[str, Iterable[str]] = None,
    relativeOrbit: Union[
        int, Tuple[int, int], Iterable[Union[int, Tuple[int, int]]]
    ] = None,
    season: Tuple[int, int] = None,
    start: Union[datetime.datetime, str] = None,
    absoluteBurstID: Union[int, Iterable[int]] = None,
    relativeBurstID: Union[int, Iterable[int]] = None,
    fullBurstID: Union[str, Iterable[str]] = None,
    collections: Union[str, Iterable[str]] = None,
    temporalBaselineDays: Union[str, Iterable[str]] = None,
    maxResults: int = None,
    opts: ASFSearchOptions = None,
) -> Generator[ASFSearchResults, None, None]:
    # Create a kwargs dict, that's all of the 'not None' items, and merge it with opts:
    kwargs = locals()
    opts = ASFSearchOptions() if kwargs["opts"] is None else copy(opts)
    del kwargs["opts"]

    kwargs = dict((k, v) for k, v in kwargs.items() if v is not None)
    kw_opts = ASFSearchOptions(**kwargs)

    # Anything passed in as kwargs has priority over anything in opts:
    opts.merge_args(**dict(kw_opts))

    maxResults = opts.pop("maxResults", None)

    if maxResults is not None and (
        getattr(opts, "granule_list", False)
        or getattr(opts, "product_list", False)
    ):
        raise ValueError(
            "Cannot use maxResults along with product_list/granule_list."
        )

    preprocess_opts(opts)

    url = "/".join(
        s.strip("/")
        for s in [f"https://{opts.host}", f"{INTERNAL.CMR_GRANULE_PATH}"]
    )
    total = 0

    queries = build_subqueries(opts)
    for query in queries:
        translated_opts = translate_opts(query)
        cmr_search_after_header = ""
        subquery_count = 0

        while cmr_search_after_header is not None:
            try:
                (
                    items,
                    subquery_max_results,
                    cmr_search_after_header,
                ) = query_cmr(
                    opts.session, url, translated_opts, subquery_count
                )
            except (ASFSearchError, CMRIncompleteError) as e:
                message = str(e)
                logging.error(message)
                report_search_error(query, message)
                opts.session.headers.pop("CMR-Search-After", None)
                return

            opts.session.headers.update(
                {"CMR-Search-After": cmr_search_after_header}
            )
            last_page = process_page(
                items,
                maxResults,
                subquery_max_results,
                total,
                subquery_count,
                opts,
            )
            subquery_count += len(last_page)
            total += len(last_page)
            last_page.searchComplete = (
                subquery_count == subquery_max_results or total == maxResults
            )
            yield last_page

            if last_page.searchComplete:
                if (
                    total == maxResults
                ):  # the user has as many results as they wanted
                    opts.session.headers.pop("CMR-Search-After", None)
                    return
                else:  # or we've gotten all possible results for this subquery
                    cmr_search_after_header = None

        opts.session.headers.pop("CMR-Search-After", None)


@retry(
    reraise=True,
    retry=retry_if_exception_type(CMRIncompleteError),
    wait=wait_fixed(2),
    stop=stop_after_attempt(3),
)
def query_cmr(
    session: ASFSession, url: str, translated_opts: dict, sub_query_count: int
):
    response = get_page(
        session=session, url=url, translated_opts=translated_opts
    )

    items = [
        ASFProductExtended(f, session=session)
        for f in response.json()["items"]
    ]
    hits: int = response.json()[
        "hits"
    ]  # total count of products given search opts

    # sometimes CMR returns results with the wrong page size
    if (
        len(items) != INTERNAL.CMR_PAGE_SIZE
        and len(items) + sub_query_count < hits
    ):
        raise CMRIncompleteError(
            f"CMR returned page of incomplete results. Expected {min(INTERNAL.CMR_PAGE_SIZE, hits - sub_query_count)} results, got {len(items)}"
        )

    return items, hits, response.headers.get("CMR-Search-After", None)


def search(
    absoluteOrbit: Union[
        int, Tuple[int, int], Iterable[Union[int, Tuple[int, int]]]
    ] = None,
    asfFrame: Union[
        int, Tuple[int, int], Iterable[Union[int, Tuple[int, int]]]
    ] = None,
    beamMode: Union[str, Iterable[str]] = None,
    beamSwath: Union[str, Iterable[str]] = None,
    campaign: Union[str, Iterable[str]] = None,
    maxDoppler: float = None,
    minDoppler: float = None,
    end: Union[datetime.datetime, str] = None,
    maxFaradayRotation: float = None,
    minFaradayRotation: float = None,
    flightDirection: str = None,
    flightLine: str = None,
    frame: Union[
        int, Tuple[int, int], Iterable[Union[int, Tuple[int, int]]]
    ] = None,
    granule_list: Union[str, Iterable[str]] = None,
    groupID: Union[str, Iterable[str]] = None,
    insarStackId: str = None,
    instrument: Union[str, Iterable[str]] = None,
    intersectsWith: str = None,
    lookDirection: Union[str, Iterable[str]] = None,
    offNadirAngle: Union[
        float, Tuple[float, float], Iterable[Union[float, Tuple[float, float]]]
    ] = None,
    platform: Union[str, Iterable[str]] = None,
    polarization: Union[str, Iterable[str]] = None,
    processingDate: Union[datetime.datetime, str] = None,
    processingLevel: Union[str, Iterable[str]] = None,
    product_list: Union[str, Iterable[str]] = None,
    relativeOrbit: Union[
        int, Tuple[int, int], Iterable[Union[int, Tuple[int, int]]]
    ] = None,
    season: Tuple[int, int] = None,
    start: Union[datetime.datetime, str] = None,
    absoluteBurstID: Union[int, Iterable[int]] = None,
    relativeBurstID: Union[int, Iterable[int]] = None,
    fullBurstID: Union[str, Iterable[str]] = None,
    collections: Union[str, Iterable[str]] = None,
    temporalBaselineDays: Union[str, Iterable[str]] = None,
    maxResults: int = None,
    opts: ASFSearchOptions = None,
) -> ASFSearchResults:
    """
    Performs a generic search using the ASF SearchAPI. Accepts a number of search parameters, and/or an ASFSearchOptions object. If an ASFSearchOptions object is provided as well as other specific parameters, the two sets of options will be merged, preferring the specific keyword arguments.

    :param absoluteOrbit: For ALOS, ERS-1, ERS-2, JERS-1, and RADARSAT-1, Sentinel-1A, Sentinel-1B this value corresponds to the orbit count within the orbit cycle. For UAVSAR it is the Flight ID.
    :param asfFrame: This is primarily an ASF / JAXA frame reference. However, some platforms use other conventions. See ‘frame’ for ESA-centric frame searches.
    :param beamMode: The beam mode used to acquire the data.
    :param beamSwath: Encompasses a look angle and beam mode.
    :param campaign: For UAVSAR and AIRSAR data collections only. Search by general location, site description, or data grouping as supplied by flight agency or project.
    :param maxDoppler: Doppler provides an indication of how much the look direction deviates from the ideal perpendicular flight direction acquisition.
    :param minDoppler: Doppler provides an indication of how much the look direction deviates from the ideal perpendicular flight direction acquisition.
    :param end: End date of data acquisition. Supports timestamps as well as natural language such as "3 weeks ago"
    :param maxFaradayRotation: Rotation of the polarization plane of the radar signal impacts imagery, as HH and HV signals become mixed.
    :param minFaradayRotation: Rotation of the polarization plane of the radar signal impacts imagery, as HH and HV signals become mixed.
    :param flightDirection: Satellite orbit direction during data acquisition
    :param flightLine: Specify a flightline for UAVSAR or AIRSAR.
    :param frame: ESA-referenced frames are offered to give users a universal framing convention. Each ESA frame has a corresponding ASF frame assigned. See also: asfframe
    :param granule_list: List of specific granules. Search results may include several products per granule name.
    :param groupID: Identifier used to find products considered to be of the same scene but having different granule names
    :param insarStackId: Identifier used to find products of the same InSAR stack
    :param instrument: The instrument used to acquire the data. See also: platform
    :param intersectsWith: Search by polygon, linestring, or point defined in 2D Well-Known Text (WKT)
    :param lookDirection: Left or right look direction during data acquisition
    :param offNadirAngle: Off-nadir angles for ALOS PALSAR
    :param platform: Remote sensing platform that acquired the data. Platforms that work together, such as Sentinel-1A/1B and ERS-1/2 have multi-platform aliases available. See also: instrument
    :param polarization: A property of SAR electromagnetic waves that can be used to extract meaningful information about surface properties of the earth.
    :param processingDate: Used to find data that has been processed at ASF since a given time and date. Supports timestamps as well as natural language such as "3 weeks ago"
    :param processingLevel: Level to which the data has been processed
    :param product_list: List of specific products. Guaranteed to be at most one product per product name.
    :param relativeOrbit: Path or track of satellite during data acquisition. For UAVSAR it is the Line ID.
    :param season: Start and end day of year for desired seasonal range. This option is used in conjunction with start/end to specify a seasonal range within an overall date range.
    :param start: Start date of data acquisition. Supports timestamps as well as natural language such as "3 weeks ago"
    :param collections: List of collections (concept-ids) to limit search to
    :param temporalBaselineDays: List of temporal baselines, used for Sentinel-1 Interferogram (BETA)
    :param maxResults: The maximum number of results to be returned by the search
    :param opts: An ASFSearchOptions object describing the search parameters to be used. Search parameters specified outside this object will override in event of a conflict.

    :return: ASFSearchResults(list) of search results
    """
    kwargs = locals()
    data = dict(
        (k, v)
        for k, v in kwargs.items()
        if k not in ["host", "opts"] and v is not None
    )

    opts = ASFSearchOptions() if opts is None else copy(opts)
    opts.merge_args(**data)

    results = ASFSearchResults([])

    # The last page will be marked as complete if results sucessful
    for page in search_generator(opts=opts):
        results.extend(page)
        results.searchComplete = page.searchComplete
        results.searchOptions = page.searchOptions

    results.sort(
        key=lambda p: (p.properties["stopTime"], p.properties["fileID"]),
        reverse=True,
    )

    return results


def granule_search(
    granule_list: Iterable[str],
    opts: ASFSearchOptions = None,
) -> ASFSearchResults:
    """
    Performs a granule name search using the ASF SearchAPI

    :param granule_list: List of specific granules. Results may include several products per granule name.
    :param opts: An ASFSearchOptions object describing the search parameters to be used. Search parameters specified outside this object will override in event of a conflict.

    :return: ASFSearchResults(list) of search results
    """

    opts = ASFSearchOptions() if opts is None else copy(opts)

    opts.merge_args(granule_list=granule_list)

    return search(opts=opts)


####


class AlaskanSateliteFacility(Provider):
    def download_many(
        self,
        search_results: List[core.models.CommonSearchResult],
        download_dir: str,
        overwrite: bool = False,
        processes: int = 6,
    ) -> None:
        """Download many files from the Alaskan Satellite Facility"""

        # Check that the provider's credentials that are needed are set
        self._check_credentials_exist()

        # Extract the file ids from the search results
        search_file_ids = [
            result.identifier
            for result in search_results
            if result.identifier is not None
        ]

        logger.info("Downloading from Alaskan Satellite Facility")
        logger.debug(f"Search file ids: {search_file_ids}")

        # Add the ASF logger to the root logger
        asf_logger = logging.getLogger("asf_search")
        asf_logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

        self.create_download_folder(download_dir)  # Create the download folder

        # Authenticate with ASF
        try:
            session = asf_search.ASFSession().auth_with_token(
                token=credentials.NASA_TOKEN,
            )

            # Search for the granules
            res = granule_search(search_file_ids)
            logger.info(
                f"Found {len(res)} files to download (may include "
                "metadata files)"
            )

            if len(res) == 0:
                logger.info("No files to download, skipping")
                return  # nothing to download

            # Download the granules using the ASF API library
            # print(dir(res), type(res))
            # sys.exit()
            res.download(
                path=download_dir, session=session, processes=processes
            )
        except asf_search.ASFAuthenticationError as e:
            logger.error(
                "ASF authentication error. Check your credentials and make "
                "sure that you have accepted the ASF EULA in your NASA "
                "profile at "
                "https://urs.earthdata.nasa.gov/users/ejayt/unaccepted_eulas"
            )
            logger.debug(f"ASF Authentication error: {e}")
            return


asf: AlaskanSateliteFacility = AlaskanSateliteFacility(
    name="Alaskan Satellite Facility",
    description="Alaskan Satellite Facility",
    uri="https://asf.alaska.edu",
    credentials_required=["NASA_TOKEN"],
)
