from typing import Tuple
from earth_extractor.satellites import enums
from earth_extractor.satellites.base import Satellite as SatelliteClass
from earth_extractor.cli_options import Satellites
import shapely
from shapely.geometry import GeometryCollection
import pyproj


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

    return shapely.from_geojson(geojson_data)


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
    projected_geom = shapely.ops.transform(transformer.transform, buffered_geom)

    return projected_geom
