#!/usr/bin/env python3
import eodag
import datetime
import typer
from typing import Annotated, List
from earth_extractor.satellites.enums import Satellite, ProcessingLevel
from earth_extractor.models import ROI
import logging
from config import constants

# Define a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(constants.LOGLEVEL_CONSOLE)
console_handler.setFormatter(constants.LOGFORMAT_CONSOLE)
logging.getLogger().addHandler(console_handler)

# Define logger for this file
logger = logging.getLogger(__name__)
logger.setLevel(constants.LOGLEVEL_CONSOLE)

# Initialise the Typer class
app = typer.Typer(no_args_is_help=True)


@app.command()
def show_providers(
    roi: Annotated[
        str,
        typer.Option("--roi",
                     help="Region of interest to consider. "
                     "Format: lon_min,lat_min,lon_max,lat_max")
    ],
    start: Annotated[
        datetime.datetime,
        typer.Option("--start",
                     help="Start datetime of the search.")
    ],
    end: Annotated[
        datetime.datetime,
        typer.Option("--end",
                     help="End datetime of the search.")
    ],
    satellites: Annotated[
        List[Satellite],
        typer.Option("--satellite",
                     help="Satellite to consider. To define the processing "
                     "levels, use the following format: "
                     "<satellite>:<level1>:<level2>. If no level is specified "
                     "a default level will be used (usually L1).")
    ],
    no_confirmation: bool = typer.Option(
        False, "--no-confirmation",
        help="Do not ask for confirmation before downloading"
    )
) -> None:
    roi_obj: ROI = ROI.from_string(roi)

    # Hold all satellite operations in a list to work on
    satellite_operations = []

    # Parse the satellite:level string into workable tuples
    for satellite in satellites:
        satellites_with_levels = satellite.split(':')
        if len(satellites_with_levels) == 1:
            satellite_operations.append(
                (satellites_with_levels[0], ProcessingLevel.L1)
            )


    # Rearrange the Satellite:Level structure into tuples
    satellite_level_choices: List[str] = []

    print(satellite_level_choices)
    product_list = []
    for product in dag.list_product_types():
        # print(product['ID'])
        # product_providers = dag.available_providers(product['ID'])

        # print(product_providers)
        if (
            (product['platform'] in satellites)
            and (product['processingLevel'] in level)
        ):

            print(f"ID: {product['ID']}", end=' ')
            print()
            product_list.append(product['ID'])

    logger.info(f"ROI: {roi_obj}")
    logger.info(f"Time: {start} {end}")
    logger.info(product_list)

    results = []
    # Search for each satellite and level and combine results
    for product_id in product_list:
        res = dag.search_all(start=start.isoformat(), end=end.isoformat(),
                             geom=roi_obj.dict(), productType=product_id)
        results += res

    # Prompt user before initiating download
    if not no_confirmation:
        input(
            f"The search found {len(results)} results. "
            "(use the --no-confirmation flag to bypass this prompt)\n"
            "Press enter to continue:"
        )

    results = results[0:2]
    paths = dag.download_all(results)

    logger.info("The output files are located at:")
    for path in paths:
        logger.info(path)


if __name__ == "__main__":
    app()
