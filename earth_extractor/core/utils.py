from typing import Tuple, List, Dict, Any, Union
from earth_extractor import core
from earth_extractor.core.models import CommonSearchResult
import logging
from earth_extractor.satellites import enums
from earth_extractor.satellites.base import Satellite
from earth_extractor.cli_options import (
    Satellites,
    TemporalFrequency,
    SatelliteChoices,
)
import shapely
import shapely.ops
from shapely.geometry import GeometryCollection
import pyproj
import datetime
import pandas as pd
from dataclasses import asdict
import requests
import os
import tqdm
import tenacity
from concurrent.futures import ThreadPoolExecutor, as_completed


# Define logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


def pair_satellite_with_level(
    choice: SatelliteChoices,
) -> Tuple[Satellite, enums.ProcessingLevel]:
    """Splits the input satellite and level choice from the command line

        Expects a `<Satellite>:<ProcessingLevel>` string.

    Parameters
    ----------
    choice : str
        The satellite and level choice from the command line

    Returns
    -------
    Tuple[Satellite, ProcessingLevel]
        A tuple containing the satellite and level choice
    """

    satellite, processing_level = choice.split(":")

    # Check if the satellite is valid, if true assign class to a variable
    if satellite not in Satellites.__members__:
        raise ValueError(
            f"Invalid satellite choice: {satellite}. "
            f"Valid choices are: {Satellites.__members__}"
        )
    else:
        satellite_choice: Satellite = Satellites[satellite].value

    # Check if the processing level is valid, if true assign enum to a variable
    if processing_level not in enums.ProcessingLevel.__members__:
        raise ValueError(
            f"Invalid processing level choice: {processing_level}. "
            f"Valid choices are: {enums.ProcessingLevel.__members__}"
        )
    else:
        level_choice: enums.ProcessingLevel = enums.ProcessingLevel[
            processing_level
        ]

    # Validate that the satellite contains the chosen level
    if level_choice not in satellite_choice.processing_levels:
        raise ValueError(
            f"The chosen processing level {level_choice} "
            f"is not available for the chosen satellite {satellite_choice}."
        )

    return (satellite_choice, level_choice)


def roi_from_geojson(geojson: str) -> GeometryCollection:
    """Extracts the ROI from a GeoJSON file

    Parameters
    ----------
    geojson : str
        The path to the GeoJSON file

    Returns
    -------
    str
        The boundary as a string
    """

    with open(geojson, "r") as in_file:
        geojson_data = in_file.read()
        geometry = shapely.from_geojson(geojson_data)

    if isinstance(geometry, shapely.GeometryCollection):
        geometry = geometry.geoms[0]
        logger.warning(
            "GeoJSON is a collection, only considering first element: "
            f"{geometry}"
        )
    if geometry is None:
        raise ValueError(
            f"Could not extract geometry from GeoJSON file: {geojson}"
        )

    return geometry


def is_float(string):
    """Checks if a string is a float"""
    try:
        float(string)
        return True
    except ValueError:
        return False


def buffer_in_metres(
    input_geom: GeometryCollection,
    buffer_metres: Union[float, int],
    crs_input: int = 4326,
    crs_output: int = 4326,
    crs_buffer: int = 3857,
) -> GeometryCollection:
    """Adds a buffer to geometry in metres

    Parameters
    ----------
    input_geom : GeometryCollection
        The geometry to buffer
    buffer_metres : Union[float, int}
        The buffer distance in metres
    crs_input : int, optional
        The CRS of the input geometry, by default 4326 (EPSG: WGS84)
    crs_output : int, optional
        The CRS of the output geometry, by default 4326 (EPSG: WGS84)
    crs_buffer : int, optional
        The CRS to execute generation of the buffer distance, by
        default 3857 (EPSG: Web Mercator), uses the same datum (WGS84) and
        units in metres

    Returns
    -------
    GeometryCollection
        The buffered geometry
    """

    logger.info(f"Applying buffer of {buffer_metres} metres to ROI")
    # Define pyproj objects for the input, buffer and output CRS
    crs_in = pyproj.CRS.from_epsg(crs_input)
    crs_conv = pyproj.CRS.from_epsg(crs_buffer)
    crs_out = pyproj.CRS.from_epsg(crs_output)

    # Perform the transformation for input
    transformer = pyproj.Transformer.from_crs(crs_in, crs_conv, always_xy=True)
    projected_geom = shapely.ops.transform(transformer.transform, input_geom)

    # Perform the buffer in the buffer CRS
    buffered_geom = projected_geom.buffer(buffer_metres)

    # Perform the transformation for output
    transformer = pyproj.Transformer.from_crs(
        crs_conv, crs_out, always_xy=True
    )
    reprojected_buffered_geom = shapely.ops.transform(
        transformer.transform, buffered_geom
    )

    logger.debug(f"Adjusted ROI (post-buffer): {reprojected_buffered_geom}")

    return reprojected_buffered_geom


def parse_roi(
    roi: str,
    buffer: float,
) -> GeometryCollection:
    """Parses the ROI input from the command line"""

    if "<" in roi or ">" in roi:
        # In the case the user explicitly inputs < or > as per the help msg
        raise ValueError("Do not include the '<' or '>' in the ROI.")

    # Check if the input is a BBox, Point or a path to a GeoJSON file
    if (len(roi.split(",")) == 4) and all(  # BBox
        [core.utils.is_float(i) for i in roi.split(",")]
    ):
        # If str splits into 4 float compatible values, consider it a BBox
        roi_obj = core.models.BBox.from_string(roi).to_shapely()
    elif (len(roi.split(",")) == 2) and all(  # Point
        [core.utils.is_float(i) for i in roi.split(",")]
    ):
        if buffer == 0:
            raise ValueError("Buffer must be greater than 0 for a point ROI.")
        roi_obj = core.models.Point.from_string(roi).to_shapely()
    else:
        # Otherwise, consider it a path to a GeoJSON file
        try:
            roi_obj = roi_from_geojson(roi)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"GeoJSON file not found: {roi}. If you are trying to "
                f"specify a BBox or Point, please ensure you are using the "
                f"correct format. See the help message for more information."
            ) from e
        if roi_obj.geom_type == "Point" and buffer == 0:
            raise ValueError("Buffer must be greater than 0 for a point ROI.")

    logger.debug(f"Input ROI: {roi_obj}")

    # Apply buffer to ROI if required
    if buffer > 0:
        roi_obj = buffer_in_metres(roi_obj, buffer)

    return roi_obj


def download_by_frequency(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    frequency: TemporalFrequency,
    query_results: List[core.models.CommonSearchResult],
    filter_field: str = "cloud_cover_percentage",
) -> List[core.models.CommonSearchResult]:
    """With the given start and end dates and a frequency, choose the
    satellite image with the best cloud_cover percentage and download it.
    If there are multiple images with the same cloud_cover percentage,
    choose the one with the least cloud_cover percentage.

    If there are multiple minimum values (for example if there are two or
    more images with the same cloud_cover percentage of 0), the latest
    image in the frequency period is chosen (this behaviour is defined by
    the pandas Grouper function).

    Parameters
    ----------
    start_date : datetime.datetime
        The start date of the search
    end_date : datetime.datetime
        The end date of the search
    frequency : TemporalFrequency
        The frequency of the search according to the enum
    query_results : List[core.models.CommonSearchResult]
        The query results, in the internal common format
    filter_field : str, optional
        The field to filter by, by default 'cloud_cover_percentage'

    Returns
    -------
    List[core.models.CommonSearchResult]
        The filtered query results
    """

    # Convert the query results to a list of dicts
    query_results_dict = [asdict(x) for x in query_results]

    # If filter_field is not in the query results, raise an error
    cleaned_query_results: List[Dict[Any, Any]] = []
    for result in query_results_dict:
        if result[filter_field] is None:
            logger.warning(
                f"Filter field {filter_field} not in query result "
                f"for ID: {result['product_id']} ({result['satellite']}), "
                "ignoring."
            )
            logger.debug(f"Query result ignored: {result}")
        else:
            cleaned_query_results.append(result)

    # Raise exception if there are no results
    if len(cleaned_query_results) == 0:
        raise ValueError(
            f"Filter field '{filter_field}', used to define this frequency "
            "filter is not in any of the query results, therefore, "
            "no results are returned and no download will be attempted. "
        )

    df = pd.DataFrame.from_dict(cleaned_query_results)
    # Set the 'time' column as the DataFrame index
    df.set_index("time", inplace=True)
    df.index = pd.to_datetime(df.index)

    date_range = pd.date_range(start_date, end_date)
    mask = (df.index > date_range[0]) & (df.index <= date_range[-1])
    df = df.loc[mask]

    # Find the minimum row for each grouping (Using name of the enum
    # supplied by the enum: D, M, W, Y), and joining back to the original df.
    # Then ilter df by frequency minimum for the 'cloud_cover_percentage' value
    filtered = df.merge(
        df.groupby(pd.Grouper(freq=frequency.name))["cloud_cover_percentage"]
        .min()
        .reset_index(),
        how="inner",
    )

    results: List[CommonSearchResult] = [
        core.models.CommonSearchResult(**x)
        for x in filtered.to_dict("records")
    ]

    for result in results:
        logger.debug(
            f"Interval filter results: {result.satellite} "
            f"({result.processing_level}), File: {result.filename}, "
            f"Time: {result.time}, "
            f"{filter_field}: {getattr(result, filter_field)}"
        )

    logger.info(
        f"Interval operation filtered {len(query_results_dict)} to "
        f"{len(results)} results on {results[0].satellite} "
        f"({results[0].processing_level})."
    )

    return results


@tenacity.retry(
    stop=tenacity.stop_after_attempt(
        core.config.constants.MAX_DOWNLOAD_ATTEMPTS
    ),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    reraise=True,
)
def download_with_progress(
    url: str,
    output_folder: str,
    headers: Dict[str, str] = {},
    overwrite: bool = False,
) -> None:
    """Downloads a file with a progress bar

    The output file is the same filename as the original, and is saved to
    the output_folder.

    This function is used for downloading binary files from data providers. If
    a HTML content-type is provided, it is assumed that the download failed
    and the function will raise an error. This is necessary to check for
    example in the case of NASA where some errors are returned as a 200: OK but
    with a HTML error message.

    Parameters
    ----------
    url : str
        The URL to download
    output_folder : str
        The output file base directory
    headers : Dict[str, str], optional
        The headers to use for the download, by default {}. This is necessary
        for some providers that require authentication.
    overwrite : bool, optional
        Whether to overwrite existing files, by default False
    """

    with requests.get(url, stream=True, headers=headers) as resp:
        resp.raise_for_status()
        total_size = int(resp.headers.get("content-length", -1))

        if "text/html" in resp.headers["Content-Type"]:
            # We definitely don't want to download HTML when
            # expecting a binary file. This is likely due to
            # an expired token, auth error or NASA issue.
            if (  # NASA Error
                "We are currently having issues verifying "
                "your request. Please try again later"
                in resp.content.decode("utf-8")
            ):
                error_msg = (
                    "NASA CMR: Server error in verifying "
                    f"request with URL '{url}'. This is most likely a server "
                    "error. Check the NASA Alerts & Issues page at "
                    "https://ladsweb.modaps.eosdis.nasa.gov/alerts-and-issues/"
                )
            else:
                error_msg = (
                    f"Server error in verifying request with URL '{url}'. "
                    f"This is most likely a server error. "
                )
            raise RuntimeError(error_msg)
        output_file = os.path.join(output_folder, url.split("/")[-1])

        # Check if the file already exists, then apply overwrite policy
        if os.path.exists(output_file):
            if overwrite is False:
                # Check length of existing file matches expected size
                local_filesize = os.path.getsize(output_file)
                if total_size != -1 and total_size != local_filesize:
                    logger.info(
                        f"File exists {output_file} but does not match "
                        f"server size (local: {local_filesize} remote: "
                        f"{total_size}). Redownloading file."
                    )
                else:
                    logger.warning(
                        f"File already exists: {output_file}, skipping "
                        "download."
                    )
                    return
            else:
                logger.warning(
                    f"File already exists: {output_file}, "
                    "overwriting existing file."
                )

        with open(output_file, "wb") as dest:
            with tqdm.tqdm(
                total=total_size,
                desc=url,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in resp.iter_content(chunk_size=4096):
                    if chunk:  # filter out keep-alive new chunks
                        size = dest.write(chunk)
                        bar.update(size)

    # Check size of downloaded file
    output_size = os.path.getsize(output_file)
    if output_size == 0:
        raise ValueError(
            f"Downloaded file {output_file} is empty, retrying download "
            f"(max {core.config.constants.MAX_DOWNLOAD_ATTEMPTS} attempts)."
        )

    if total_size != -1 and total_size != os.path.getsize(output_file):
        raise ValueError(
            f"Downloaded file {output_file} is not the expected size, "
            f"retrying download"
        )
    logger.debug(f"Downloaded file: {output_file}, size: {output_size}")

    return


def download_parallel(
    urls: List[str],
    output_folder: str,
    headers: Dict[str, str] = {},
    overwrite: bool = False,
    processes: int = core.constants.DEFAULT_DOWNLOAD_THREADS,
) -> None:
    """Downloads the given URLs in parallel

    Giving a total progress bar for all downloads, and overall if possible.

    Parameters
    ----------
    urls : List[str]
        A list of URLs to download
    output_folder : str
        The output file base directory
    headers : Dict[str, str], optional
        The headers to use for the download, by default {}. This is necessary
        for some providers that require authentication.
    overwrite : bool, optional
        Whether to overwrite existing files, by default False
    processes : int, optional
        The number of processes to use for downloading, by default
        core.constants.DEFAULT_DOWNLOAD_THREADS
    """

    with ThreadPoolExecutor(max_workers=processes) as executor:
        # Map download_item function to the URLs in the specified column
        futures = {
            executor.submit(
                download_with_progress, url, output_folder, headers, overwrite
            ): url
            for url in urls
        }

        # Retrieve the results as they become available
        for future in as_completed(futures):
            url = futures[future]
            try:
                result = future.result()
                logger.debug(
                    f"Downloaded file successfully (threading): {url} "
                    f"({result})"
                )
            except Exception as e:
                logger.error(f"{url} generated an exception: {e}")


def download_all_satellites_in_parallel(
    query_results: List[Tuple[Satellite, List[CommonSearchResult]]],
    output_folder: str,
    overwrite: bool = False,
) -> None:
    """Executes each provider download function in parallel

    As each provider has a different method, this function does not attempt
    to consolidate one big list, but issue the `download_many()` into
    many threads so they can all run at the same time.

    It is up to this `download_many()` function to provide parallel downloads
    for that individual provider.

    Parameters
    ----------
    query_results : List[Tuple[Satellite, List[CommonSearchResult]]]
        The query results, in the internal common format
    output_folder : str
        The output file base directory
    overwrite : bool, optional
        Whether to overwrite existing files, by default False
    """

    with ThreadPoolExecutor(
        max_workers=core.constants.DEFAULT_DOWNLOAD_THREADS
    ) as executor:
        # Map download_item function to the URLs in the specified column
        # satellite, results = query_results
        futures = {
            executor.submit(
                satgroup[0].download_many,
                search_results=satgroup[1],
                download_dir=output_folder,
                overwrite=overwrite,
            ): satgroup
            for satgroup in query_results
        }

        # Retrieve the results as they become available
        for future in as_completed(futures):
            url = futures[future]
            try:
                result = future.result()
                logger.debug(
                    f"Downloaded file successfully (threading): {url} "
                    f"({result})"
                )
            except Exception as e:
                logger.error(f"{url} generated an exception: {e}")


def download(query_results, output_dir, parallel=False, overwrite=False):
    """The main download function called by the app

    This consolidates the parallel, overwrite functionality and logging that
    became large enough for the routines that exist in 3+ different CLI
    commands.

    Parameters
    ----------
    query_results : List[Tuple[Satellite, List[CommonSearchResult]]]
        The query results, in the internal common format
    output_dir : str
        The output file base directory
    parallel : bool, optional
        Whether to download in parallel, by default False
    overwrite : bool, optional
        Whether to overwrite existing files, by default False

    """

    if parallel is True:
        # Download all of the satellites in parallel at the same time
        download_all_satellites_in_parallel(
            query_results,
            output_dir,
            overwrite=overwrite,
        )
    else:
        # Download the results using the satellite's download provider
        for sat, res in query_results:
            if len(res) > 0:
                logger.info(
                    f"Downloading results for {sat}..." f"({len(res)} items)"
                )

                # Download the results
                sat.download_many(
                    search_results=res,
                    download_dir=output_dir,
                    overwrite=overwrite,
                )
    logger.info(
        f"Download complete. Your files are in {os.path.abspath(output_dir)}"
    )
