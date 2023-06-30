#!/usr/bin/env python3
import datetime
import typer
from typing import Annotated, List, Tuple
from earth_extractor.satellites import enums
from earth_extractor.models import ROI
from earth_extractor.satellites.base import Satellite as SatelliteClass
import logging
from earth_extractor.config import constants
from earth_extractor.core.credentials import credentials
from earth_extractor.core.credentials import show_credential_list, set_all_credentials
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
def download(
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
    output_dir: str = typer.Option(
        constants.DEFAULT_DOWNLOAD_DIR,
        help="Output directory for the downloaded files."
    ),
    cloud_cover: int = typer.Option(
        100, "--cloud-cover", help="Maximum cloud cover percentage."
    ),
    no_confirmation: bool = typer.Option(
        False, "--no-confirmation",
        help="Do not ask for confirmation before downloading"
    )
) -> None:
    roi_obj: ROI = ROI.from_tuple(roi)
    logger.info(f"ROI: {roi_obj}")

    # Parse the satellite:level string into a list of workable tuples
    satellite_operations = []
    for sat in satellites:
        satellite_operations.append(pair_satellite_with_level(sat))

    # Perform a query for each satellite and level and append it to a list
    all_results = []
    for sat, level in satellite_operations:
        logger.info(f"Satellite: {sat}, Level: {level.value}")
        res = sat.query(
            processing_level=level,
            roi=roi_obj,
            start_date=start,
            end_date=end,
            cloud_cover=cloud_cover)
        logger.info(f"{sat}: Results qty {len(res)}")

        # Append results to a list with associated satellite in order to use
        # its defined download provider
        all_results.append((sat, res))

    # Sum results from all query results
    total_qty = sum([len(res) for sat, res in all_results])

    logger.info(f"Total results qty: {total_qty}")
    logger.info(f"ROI: {roi_obj}")
    logger.info(f"Time: {start} {end}")

    # Prompt user for confirmation before downloading
    if not no_confirmation:
        typer.confirm(
            "Do you want to download the results? (use --no-confirmation to "
            "skip this prompt)", abort=True
        )

    # Download the results using the satellite's download provider
    for sat, res in all_results:
        if len(res) > 0:
            logger.info(f"Downloading results for {sat}..."
                        f"({len(res)} items)")
            sat.download_many(
                search_results=res,
                download_dir=output_dir,
            )


@app.command()
def credentials(
    set_all: bool = typer.Option(
        False, help="Set all credentials"
    )
) -> None:
    ''' Management of service credential keys'''

    if set_all is True:
        logger.info("Setting credentials")
        set_all_credentials()

    show_credential_list()


@app.callback()
def menu():
    pass

def main() -> None:
    app()

if __name__ == "__main__":
    main()
