from typing import Tuple, List, Any
from earth_extractor import core
import logging
from earth_extractor.satellites import enums
from earth_extractor.satellites.base import Satellite as SatelliteClass
from earth_extractor.cli_options import Satellites, TemporalFrequency
import shapely
from shapely.geometry import GeometryCollection
import pyproj
import datetime
import enum

# Define logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_CONSOLE)


def pair_satellite_with_level(
    choice: str
) -> Tuple[SatelliteClass, enums.ProcessingLevel]:
    ''' Splits the input satellite and level choice from the command line

        Expects a `<Satellite>:<ProcessingLevel>` string.

    Parameters
    ----------
    choice : str
        The satellite and level choice from the command line

    Returns
    -------
    Tuple[Satellite, ProcessingLevel]
        A tuple containing the satellite and level choice
    '''

    satellite, processing_level = choice.split(":")

    # Check if the satellite is valid, if true assign class to a variable
    if satellite not in Satellites.__members__:
        raise ValueError(
            f"Invalid satellite choice: {satellite}. "
            f"Valid choices are: {Satellites.__members__}"
        )
    else:
        satellite_choice: SatelliteClass = Satellites[satellite].value

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


def roi_from_geojson(
    geojson: str
) -> GeometryCollection:
    ''' Extracts the ROI from a GeoJSON file

    Parameters
    ----------
    geojson : str
        The path to the GeoJSON file

    Returns
    -------
    str
        The boundary as a string
    '''

    with open(geojson, "r") as in_file:
        geojson_data = in_file.read()
        geometry = shapely.from_geojson(geojson_data)

    if isinstance(geometry, shapely.GeometryCollection):
        geometry = geometry.geoms[0]
        logger.warning(
            "GeoJSON is a collection, only considering first element:"
            f"{geometry}")


    return geometry


def is_float(string):
    ''' Checks if a string is a float '''
    try:
        float(string)
        return True
    except ValueError:
        return False


def buffer_in_metres(
    input_geom: GeometryCollection,
    buffer_metres: float | int,
    crs_input: int = 4326,
    crs_output: int = 4326,
    crs_buffer: int = 3857,
) -> GeometryCollection:
    ''' Adds a buffer to geometry in metres

    Parameters
    ----------
    input_geom : GeometryCollection
        The geometry to buffer
    buffer_metres : float | int
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
    '''

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

    logger.info(f"Adjusted ROI (post-buffer): {reprojected_buffered_geom}")

    return reprojected_buffered_geom


def parse_roi(
    roi: str,
    buffer: float,
) -> GeometryCollection:
    ''' Parses the ROI input from the command line '''

    if "<" in roi or ">" in roi:
        # In the case the user explicitly inputs < or > as per the help msg
        raise ValueError("Do not include the '<' or '>' in the ROI.")

    # Check if the input is a BBox, Point or a path to a GeoJSON file
    if (  # BBox
        (len(roi.split(',')) == 4)
        and all([core.utils.is_float(i) for i in roi.split(',')])
    ):
        # If str splits into 4 float compatible values, consider it a BBox
        roi_obj = core.models.BBox.from_string(roi).to_shapely()
    elif (  # Point
        (len(roi.split(',')) == 2)
        and all([core.utils.is_float(i) for i in roi.split(',')])
    ):
        if buffer == 0:
            raise ValueError(
                "Buffer must be greater than 0 for a point ROI."
            )
        roi_obj = core.models.Point.from_string(roi).to_shapely()
    else:
        # Otherwise, consider it a path to a GeoJSON file
        roi_obj = roi_from_geojson(roi)
        print(roi_obj.geom_type)
        print(type(roi_obj))
        if roi_obj.geom_type == 'Point' and buffer == 0:
            raise ValueError(
                "Buffer must be greater than 0 for a point ROI."
            )

    logger.info(f"Input ROI: {roi_obj}")

    # Apply buffer to ROI if required
    if buffer > 0:
        roi_obj = buffer_in_metres(roi_obj, buffer)

    return roi_obj


def download_by_frequency(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    frequency: TemporalFrequency,
    query_results: List[Any]
):
    ''' With the given start and end dates, using a frequency, choose the
        satellite image with the best cloud_cover percentage and download it.
        If there are multiple images with the same cloud_cover percentage,
        choose the one with the least cloud_cover percentage.

    '''

    # Get the frequency as a timedelta
    if frequency == TemporalFrequency.DAILY:
        freq = datetime.timedelta(days=1)
    elif frequency == TemporalFrequency.WEEKLY:
        freq = datetime.timedelta(days=7)
    elif frequency == TemporalFrequency.MONTHLY:
        freq = datetime.timedelta(days=30)
    elif frequency == TemporalFrequency.YEARLY:
        freq = datetime.timedelta(days=365)
    else:
        raise ValueError(
            f"Invalid frequency choice: {frequency}. "
            f"Valid choices are: {TemporalFrequency.__members__}"
        )

    # Create a list of dates between the start and end dates
    dates = []
    while start_date <= end_date:
        dates.append(start_date)
        start_date += freq

    # Create a list of images that match the dates
    images = []
    for date in dates:
        for image in query_results:
            if date.date() == image.date:
                images.append(image)


    ## Filter through search results for cloud cover percentage
    ## (other filters, too?)