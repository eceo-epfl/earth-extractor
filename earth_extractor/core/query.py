#!/usr/bin/env python3
import datetime
from typing import List, Tuple, Dict, Optional
import logging
from earth_extractor import core, cli_options
import os
import sys
import orjson
from earth_extractor.satellites import enums
from earth_extractor.satellites.base import Satellite
from earth_extractor.core.models import CommonSearchResult
import geopandas as gpd
import pandas as pd


# Define logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


def construct_geojson(
    gdf: gpd.GeoDataFrame,
    satellites: List[str],
    roi: str,
    buffer: float,
    cloud_cover: int,
    start: datetime.datetime,
    end: datetime.datetime,
    interval_frequency: Optional[cli_options.TemporalFrequency] = None,
    output_file: Optional[str] = None,
) -> None:
    """Converts a geodataframe to geojson

    If output_dir is empty, the geojson is printed to stdout. If output_dir
    is not empty, the geojson is exported to a file.

    The additional parameters are added to the geojson as the original query
    parameters in the metadata section `query_parameters`.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        The GeoDataFrame
    satellites : List[str]
        The satellites IDs as a list of strings
    roi : str
        The ROI
    buffer : float
        The buffer
    cloud_cover : int
        The cloud cover
    start : datetime.datetime
        The start date
    end : datetime.datetime
        The end date
    interval_frequency : Optional[cli_options.TemporalFrequency], optional
        The interval frequency, by default None
    output_file : Optional[str], optional
        The output filename, by default None. If None, the geojson is printed
        to stdout

    """

    geojson_data = orjson.loads(gdf.to_json())
    geojson_data["query_parameters"] = {
        "satellites": satellites,
        "roi": roi,
        "buffer": buffer,
        "cloud_cover": cloud_cover,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "interval_frequency": (
            interval_frequency.value if interval_frequency else None
        ),
    }
    if output_file is None:
        # Print the geojson to stdout (PIPE option)
        print(orjson.dumps(geojson_data).decode("utf-8"))
    else:
        logger.info(f"Exporting results to GeoJSON: {output_file}")

        # Export the geojson to a file with an indent of 2 spaces
        with open(os.path.join(output_file), "wb") as f:
            f.write(orjson.dumps(geojson_data, option=orjson.OPT_INDENT_2))


def convert_query_results_to_geodataframe(
    query_results: List[CommonSearchResult],
) -> gpd.GeoDataFrame:
    """Converts the query results to a GeoDataFrame

    Parameters
    ----------
    query_results : List[CommonSearchResult]
        The query results

    Returns
    -------
    gpd.GeoDataFrame
        The query results as a GeoDataFrame
    """

    # Convert the query results to a list of dicts
    query_results_geojson = [x.to_geojson() for x in query_results]

    # Convert the query results to a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_dict(query_results_geojson)

    return gdf


def convert_geodataframe_to_query_results(
    gdf: gpd.GeoDataFrame,
) -> List[CommonSearchResult]:
    """Converts the GeoDataFrame to query results

    A reverse of the `convert_query_results_to_geodataframe` function, used
    in importing the exported GeoJSON files.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        The GeoDataFrame

    Returns
    -------
    List[CommonSearchResult]
        The query results
    """

    # Convert the GeoDataFrame to a list of dicts
    query_results = [x for x in gdf.to_dict("records")]
    query_results = []
    for idx, row in gdf.iterrows():
        query_results.append(
            CommonSearchResult(
                satellite=row["satellite"],
                product_id=row["product_id"],
                link=row["link"],
                identifier=row["identifier"],
                filename=row["filename"],
                time=row["time"],
                cloud_cover_percentage=row["cloud_cover_percentage"],
                size=row["size"],
                processing_level=row["processing_level"],
                sensor=row["sensor"],
                geometry=row["geometry"],
            )
        )

    return query_results


def batch_query(
    start: datetime.datetime,
    end: datetime.datetime,
    satellites: List[cli_options.SatelliteChoices],
    roi: str,
    buffer: float,
    output_dir: str,
    cloud_cover: int,
    export: cli_options.ExportMetadataOptions,
    results_only: bool,
    interval_frequency: Optional[cli_options.TemporalFrequency] = None,
) -> List[Tuple[Satellite, List[CommonSearchResult]]]:
    if results_only:
        if export == cli_options.ExportMetadataOptions.DISABLED.value:
            raise ValueError("Cannot use --results-only without --export")
        logger.info("Skipping download, only exporting results")

    if interval_frequency is None:
        logger.info("Starting Earth Extractor batch mode")
    else:
        logger.info(
            "Starting Earth Extractor interval-batch mode with "
            f"interval frequency {interval_frequency.value}"
        )

    logger.info(f"Time: {start} {end}")
    roi_obj = core.utils.parse_roi(roi, buffer)

    # Parse the satellite:level string into a list of workable tuples
    satellite_operations: List[Tuple[Satellite, enums.ProcessingLevel]] = []

    # Create a list of tuples of satellites and levels
    for sat in satellites:
        satellite_operations.append(core.utils.pair_satellite_with_level(sat))

    # Perform a query for each satellite and level and append it to a list
    all_results = []

    # Create an empty geodataframe to hold data that can be appended
    # with all the satellite results
    gdf_all = gpd.GeoDataFrame()

    # Process each satellite and level
    for sat, level in satellite_operations:
        logger.debug(
            f"Querying satellite Satellite: {sat}, Level: {level.value}"
        )

        if cloud_cover < 100 and not sat.has_cloud_cover:
            logger.warning(
                f"Satellite {sat} does not support cloud cover filtering. "
                "Ignoring the filter and continuing."
            )
        # If the satellite does not have a cloud_cover query parameter, set it
        # to None
        res = sat.query(
            processing_level=level,
            roi=roi_obj,
            start_date=start,
            end_date=end,
            cloud_cover=cloud_cover if sat.has_cloud_cover else None,
        )

        if interval_frequency is not None:
            # If interval frequency is set, then we need to query the results
            # by the frequency
            res = core.utils.download_by_frequency(
                start_date=start,
                end_date=end,
                frequency=interval_frequency,
                query_results=res,
                filter_field="cloud_cover_percentage",
            )

        msg_summary = (
            f"Satellite: {sat}, Level: {level.value}. "
            f"Results qty: ({len(res)})"
        )

        # If the user wants to export the results, do so
        if export != cli_options.ExportMetadataOptions.DISABLED.value:
            # Add the results to the geodataframe
            results = convert_query_results_to_geodataframe(res)
            if not results.empty:
                gdf_all = pd.concat([gdf_all, results])
            else:
                logger.info(
                    f"No results for satellite {sat} and level {level.value}"
                )
                continue

            if sat == cli_options.Satellites.SWISSIMAGE.value:
                # Warn the user that swiss image 10 and 200cm data is not
                # going to have the correct geometry. Do this only in the
                # FILE output as to not corrupt the PIPE output.
                logger.warning(
                    "Due to the limits of the SwissImage API, the "
                    "boundaries of SwissImage will reflect only the "
                    "geometry of the given ROI in the query. See comments "
                    "within the code for more information."
                )
        logger.info(msg_summary)  # As to not pollute PIPE output

        # Append results to a list with associated satellite in order to use
        # its defined download provider
        all_results.append((sat, res))

    if export != cli_options.ExportMetadataOptions.DISABLED.value:
        satellite_list = [sat.value for sat in satellites]
        output_file = None  # Default PIPE output

        if export == cli_options.ExportMetadataOptions.FILE.value:
            # Remove millisecondsfrom the timestamp
            timestamp = core.config.constants.COMMON_TIMESTAMP.split(".")[0]
            timestamp = timestamp.replace("-", "")  # Remove symbols
            output_file = os.path.join(
                # Common timestamp without milliseconds and with summary
                # of satellites
                # eg: 20230824T085346_swissimage-cm200_swissimage-cm10.geojson
                output_dir,
                f"{timestamp}_"
                f"{'_'.join(satellite_list).replace(':', '-').lower()}"
                f".geojson",
            )

        construct_geojson(
            gdf=gdf_all,
            satellites=satellite_list,
            roi=roi,
            buffer=buffer,
            cloud_cover=cloud_cover,
            start=start,
            end=end,
            interval_frequency=interval_frequency,
            output_file=output_file,
        )

    if results_only or export == cli_options.ExportMetadataOptions.PIPE.value:
        """Exit on results only or PIPE export

        If the application does not exit on PIPE, the user's command will
        not stop executing
        """
        sys.exit()

    return all_results


def import_query_results(
    geojson_file: str,
) -> List[Tuple[Satellite, List[CommonSearchResult]]]:
    """Import a geojson file, convert it CommonSearchResult objects"""
    logger.info("Starting Earth Extractor import mode")
    logger.info(f"Importing geojson file: {geojson_file}")

    # Read the geojson file
    import geopandas

    gdf = geopandas.read_file(geojson_file)

    # Convert the geojson file to a list of CommonSearchResult objects
    results = convert_geodataframe_to_query_results(gdf)

    # Create a tuple of satellite and grouping of its results
    satellite_groups: Dict[Satellite, List[CommonSearchResult]] = {}
    for result in results:
        satellite_choice = cli_options.Satellites[result.satellite].value

        # Add satellite to dict if not already present
        if satellite_choice not in satellite_groups:
            satellite_groups[satellite_choice] = []
        # Add result to satellite group list
        satellite_groups[satellite_choice].append(result)

    # Convert the dict to a list of tuples
    query_results = [(key, rows) for key, rows in satellite_groups.items()]

    total_qty = sum([len(res) for sat, res in query_results])
    logger.info(
        f"Imported {total_qty} records from {len(query_results)} "
        f"satellite{'(s)' if len(query_results) > 1 else ''}"
    )
    return query_results
