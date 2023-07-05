#!/usr/bin/env python3
import datetime
import typer
from shapely.geometry.collection import GeometryCollection
from typing import Annotated, List, Tuple
from earth_extractor.core.models import BBox
import logging
from earth_extractor import core
from earth_extractor.cli_options import SatelliteChoices
from earth_extractor.core.utils import pair_satellite_with_level
import atexit

# Define a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(core.config.constants.LOGLEVEL_CONSOLE)
console_handler.setFormatter(core.config.constants.LOGFORMAT_CONSOLE)
logging.getLogger().addHandler(console_handler)

# Define a file handler for ERRORs
error_handler = core.logging.ErrorFlagHandler()  # Watches for ERRORs
logging.getLogger().addHandler(error_handler)
atexit.register(error_handler.print_status)  # Print error status on exit

# Define logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_CONSOLE)

# Setup the file logger
core.logging.setup_file_logger('.')

# Initialise the Typer class
app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def download(
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
    roi: Annotated[    # Multichoice types are not possible yet, take a str
        str,           # then parse option in function
        typer.Option(  # https://github.com/tiangolo/typer/issues/140
        "--roi",
        help="Region of interest to consider. "
             "Format: lon_min,lat_min,lon_max,lat_max or path to a GeoJSON "
             "file (eg. bounds.json).")
    ],
    output_dir: str = typer.Option(
        core.config.constants.DEFAULT_DOWNLOAD_DIR,
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
    if (
        (len(roi.split(',')) == 4)
        and all([core.utils.is_float(i) for i in roi.split(',')])
    ):
        # If str splits into 4 numeric values, consider it a BBox
        roi_obj: GeometryCollection = BBox.from_string(roi).to_shapely()
    else:
        # Otherwise, consider it a path to a GeoJSON file
        roi_obj: GeometryCollection = core.utils.roi_from_geojson(roi)

    logger.info(f"ROI: {roi_obj}")
    logger.info(f"Time: {start} {end}")

    # Parse the satellite:level string into a list of workable tuples
    satellite_operations = []
    for sat in satellites:
        satellite_operations.append(pair_satellite_with_level(sat))

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
        logger.info(
            f"Satellite: {sat}, Level: {level.value}.\tQty ({len(res)})"
        )

        # Append results to a list with associated satellite in order to use
        # its defined download provider
        all_results.append((sat, res))

    # Sum results from all query results
    total_qty = sum([len(res) for sat, res in all_results])

    logger.info(f"Total results qty: {total_qty}")

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
    delete: str = typer.Option(
        None, help="Value to delete"
    ),
    set: bool = typer.Option(
        False, help="Set all credentials"
    ),
    show_secrets: bool = typer.Option(
        False, help="Display values of saved secrets"
    ),
) -> None:
    ''' Management of service credential keys'''

    if set:
        logger.info("Setting credentials. Press enter to accept default "
                    "value given in brackets.")
        core.credentials.set_all_credentials()

    if delete:
        core.credentials.delete_credential(delete)

    core.credentials.show_credential_list(show_secret=show_secrets)


@app.callback()
def menu():
    ''' The main menu of Typer

    The @app.command() decorated functions are the subcommands of this menu.
    '''
    logger.info('Starting Earth Extractor')


def main() -> None:
    ''' The main function of the application

    Used by the poetry entrypoint.
    '''

    app()


if __name__ == "__main__":
    main()
