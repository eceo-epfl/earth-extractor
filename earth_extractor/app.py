#!/usr/bin/env python3
import eodag
import datetime
import typer
from typing import Annotated, List, Tuple
from earth_extractor.satellites import enums
from earth_extractor.models import ROI
from earth_extractor.satellites.base import Satellite as SatelliteClass
import logging
from earth_extractor.config import constants
from earth_extractor.cli_options import SatelliteChoices, Satellites
from earth_extractor.utils import pair_satellite_with_level


# Define a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(constants.LOGLEVEL_CONSOLE)
console_handler.setFormatter(constants.LOGFORMAT_CONSOLE)
logging.getLogger().addHandler(console_handler)

# Define logger for this file
logger = logging.getLogger(__name__)
logger.setLevel(constants.LOGLEVEL_CONSOLE)

# Initialise the Typer class
app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def show_providers(
    roi: Annotated[
        Tuple[float, float, float, float],
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
        List[SatelliteChoices],
        typer.Option("--satellite",
                     help="Satellite to consider. To add multiple satellites, "
                     "use the option multiple times.")
    ],
    no_confirmation: bool = typer.Option(
        False, "--no-confirmation",
        help="Do not ask for confirmation before downloading"
    )
) -> None:
    roi_obj: ROI = ROI.from_tuple(roi)
    logger.info(f"ROI: {roi_obj}")
    # Parse the satellite:level string into a lsit of workable tuples
    satellite_operations = []
    for sat in satellites:
        satellite_operations.append(pair_satellite_with_level(sat))

    for sat, level in satellite_operations:
        logger.info(f"Satellite: {sat}, Level: {level.value}")
        res = sat.query(processing_level=level, roi=roi_obj,
                        start_date=start, end_date=end)
        logger.info(f"{sat}: Results qty {len(res)}")
        print(list(res.items())[0])

    logger.info(f"ROI: {roi_obj}")
    logger.info(f"Time: {start} {end}")
    # logger.info(product_list)

    # results = []
    # # Search for each satellite and level and combine results
    # for product_id in product_list:
    #     res = dag.search_all(start=start.isoformat(), end=end.isoformat(),
    #                          geom=roi_obj.dict(), productType=product_id)
    #     results += res

    # # Prompt user before initiating download
    # if not no_confirmation:
    #     input(
    #         f"The search found {len(results)} results. "
    #         "(use the --no-confirmation flag to bypass this prompt)\n"
    #         "Press enter to continue:"
    #     )

    # results = results[0:2]
    # paths = dag.download_all(results)

    # logger.info("The output files are located at:")
    # for path in paths:
    #     logger.info(path)


if __name__ == "__main__":
    app()
