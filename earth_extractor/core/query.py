#!/usr/bin/env python3
import datetime
from typing import List, Tuple, Dict
import logging
from earth_extractor import core, cli_options
import os
import sys
from earth_extractor.satellites import enums
from earth_extractor.satellites.base import Satellite
from earth_extractor.core.models import CommonSearchResult
import geopandas as gpd


# Define logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


def export_query_results_to_geojson(
    gdf: gpd.GeoDataFrame,
    output_dir: str,
) -> None:
    # Convert the results to a GeoDataFrame

    output_file = os.path.join(
        output_dir,
        core.config.constants.GEOJSON_EXPORT_FILENAME
    )
    logger.info(f"Exporting results to GeoJSON: {output_file}")
    gdf.to_file(
        output_file,
        driver='GeoJSON'
    )


def convert_query_results_to_geodataframe(
    query_results: List[CommonSearchResult]
) -> gpd.GeoDataFrame:
    ''' Converts the query results to a GeoDataFrame

    Parameters
    ----------
    query_results : List[CommonSearchResult]
        The query results

    Returns
    -------
    gpd.GeoDataFrame
        The query results as a GeoDataFrame
    '''

    # Convert the query results to a list of dicts
    query_results = [x.to_geojson() for x in query_results]

    # Convert the query results to a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_dict(query_results)

    return gdf


def convert_geodataframe_to_query_results(
    gdf: gpd.GeoDataFrame
) -> List[CommonSearchResult]:
    ''' Converts the GeoDataFrame to query results

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
    '''

    # Convert the GeoDataFrame to a list of dicts
    query_results = [x for x in gdf.to_dict('records')]
    query_results = []
    for idx, row in gdf.iterrows():
        query_results.append(
            CommonSearchResult(
                satellite=row['satellite'],
                product_id=row['product_id'],
                link=row['link'],
                identifier=row['identifier'],
                filename=row['filename'],
                time=row['time'],
                cloud_cover_percentage=row['cloud_cover_percentage'],
                size=row['size'],
                processing_level=row['processing_level'],
                sensor=row['sensor'],
                geometry=row['geometry']
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
    interval_frequency: cli_options.TemporalFrequency | None = None,
) -> List[Tuple[Satellite, List[CommonSearchResult]]]:

    if results_only:
        if export == cli_options.ExportMetadataOptions.DISABLED.value:
            raise ValueError("Cannot use --results-only without --export")
        logger.info("Skipping download, only exporting results")

    if interval_frequency is None:
        logger.info('Starting Earth Extractor batch mode')
    else:
        logger.info(
            'Starting Earth Extractor interval-batch mode with '
            f'interval frequency {interval_frequency.value}'
        )

    logger.info(f"Time: {start} {end}")
    roi_obj = core.utils.parse_roi(roi, buffer)

    # Parse the satellite:level string into a list of workable tuples
    satellite_operations: List[Tuple[Satellite, enums.ProcessingLevel]] = []

    # Create a list of tuples of satellites and levels
    for sat in satellites:
        satellite_operations.append(
            core.utils.pair_satellite_with_level(sat)
        )

    # Perform a query for each satellite and level and append it to a list
    all_results = []
    for sat, level in satellite_operations:
        logger.debug(
            f"Querying satellite Satellite: {sat}, Level: {level.value}"
        )

        res = sat.query(
            processing_level=level,
            roi=roi_obj,
            start_date=start,
            end_date=end,
            cloud_cover=cloud_cover)

        # Translate the results into an internal workable format
        translated = sat._query_provider.translate_search_results(res)

        if interval_frequency is not None:
            # If interval frequency is set, then we need to query the results
            # by the frequency
            translated = core.utils.download_by_frequency(
                start_date=start,
                end_date=end,
                frequency=interval_frequency,
                query_results=translated,
                filter_field='cloud_cover_percentage'
            )

        # If the user wants to export the results, do so
        if export != cli_options.ExportMetadataOptions.DISABLED.value:
            # Convert the results to a GeoDataFrame
            gdf = convert_query_results_to_geodataframe(translated)

            if export == cli_options.ExportMetadataOptions.PIPE.value:
                logger.info("Printing GeoJSON results to console")
                print(gdf.to_json())
            elif export == cli_options.ExportMetadataOptions.FILE.value:
                export_query_results_to_geojson(gdf, output_dir)

        if results_only:
            sys.exit()

        logger.info(
            f"Satellite: {sat}, Level: {level.value}.\tQty ({len(res)})"
        )

        # Append results to a list with associated satellite in order to use
        # its defined download provider
        all_results.append((sat, translated))

    # Sum results from all query results
    total_qty = sum([len(res) for sat, res in all_results])

    logger.info(f"Total results qty: {total_qty}")

    return all_results


def import_query_results(
    geojson_file: str,
) -> List[Tuple[Satellite, List[CommonSearchResult]]]:
    ''' Import a geojson file, convert it CommonSearchResult objects  '''
    logger.info('Starting Earth Extractor import mode')
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
        satellite_groups[satellite_choice].append(
            result
        )

    # Convert the dict to a list of tuples
    query_results = [(key, rows) for key, rows in satellite_groups.items()]

    total_qty = sum([len(res) for sat, res in query_results])
    logger.info(f"Imported {total_qty} records from {len(query_results)} "
                f"satellite{'(s)' if len(query_results) > 1 else ''}")
    return query_results
