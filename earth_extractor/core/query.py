#!/usr/bin/env python3
import datetime
import typer
from typing import Annotated, List, Dict, Any, Tuple
import logging
from earth_extractor import core, cli_options
import atexit
import os
import sys
from earth_extractor.satellites import enums
from earth_extractor.satellites.base import Satellite

# Define logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


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
) -> List[Tuple[Satellite, List[core.models.CommonSearchResult]]]:

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

        # If the user wants to export the results, do so
        if export != cli_options.ExportMetadataOptions.DISABLED.value:
            # Convert the results to a GeoDataFrame
            gdf = core.utils.convert_query_results_to_geodataframe(translated)

            if export == cli_options.ExportMetadataOptions.PIPE.value:
                logger.info("Printing GeoJSON results to console")
                print(gdf.to_json())
            elif export == cli_options.ExportMetadataOptions.FILE.value:
                output_file = os.path.join(
                    output_dir,
                    core.config.constants.GEOJSON_EXPORT_FILENAME
                )
                logger.info(f"Exporting results to GeoJSON: {output_file}")
                gdf.to_file(
                    output_file,
                    driver='GeoJSON'
                )

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
