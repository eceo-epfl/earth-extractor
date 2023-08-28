#!/usr/bin/env python3
import datetime
import typer
from typing import Annotated, List
import logging
from earth_extractor import core, cli_options, __version__
import atexit
import os
import sys


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
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


# Initialise the Typer class
app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_show_locals=False,
)


@app.command()
def import_geojson(
    filename: str = typer.Option(
        ..., help="Path to the GeoJSON file to import"
    ),
    output_dir: str = typer.Option(
        core.config.constants.DEFAULT_DOWNLOAD_DIR,
        help="Output directory for the downloaded files.",
    ),
    no_confirmation: bool = typer.Option(
        False,
        "--no-confirmation",
        help="Do not ask for confirmation before downloading",
    ),
    parallel: bool = typer.Option(
        True, help="Download all results in parallel"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing files in the output directory",
    ),
) -> None:
    """Import a GeoJSON file with metadata to the database

    The GeoJSON file must be in the same format as the one exported by the
    export command.
    """

    # Check if the file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    # Import the GeoJSON file
    query_results = core.query.import_query_results(geojson_file=filename)

    # Prompt user for confirmation before downloading
    if not no_confirmation:
        typer.confirm(
            "Do you want to download the results? (use --no-confirmation to "
            "skip this prompt)",
            abort=True,
        )

    core.utils.download(query_results, output_dir, parallel, overwrite)


@app.command()
def batch(
    start: Annotated[
        datetime.datetime,
        typer.Option("--start", help="Start datetime of the search."),
    ],
    end: Annotated[
        datetime.datetime,
        typer.Option("--end", help="End datetime of the search."),
    ],
    satellites: Annotated[
        List[cli_options.SatelliteChoices],
        typer.Option(
            "--satellite",
            help="Satellite to consider. To add multiple satellites, "
            "use the option multiple times.",
            case_sensitive=False,
        ),
    ],
    roi: Annotated[  # Multichoice types are not possible yet, take a str
        str,  # then parse option in function
        typer.Option(  # https://github.com/tiangolo/typer/issues/140
            "--roi",
            help="Region of interest to consider. "
            "Format: <lon_min,lat_min,lon_max,lat_max> for boundary, "
            "<lon,lat> for a point, or path to a "
            "GeoJSON file (eg. <bounds.json>). All inputs are assumed to be "
            "projected in WGS84 (EPSG: 4326), and all point geometries must "
            "also use the buffer option.",
        ),
    ],
    buffer: float = typer.Option(
        0.0, "--buffer", help="Buffer to apply to the ROI in metres."
    ),
    output_dir: str = typer.Option(
        core.config.constants.DEFAULT_DOWNLOAD_DIR,
        help="Output directory for the downloaded files.",
    ),
    cloud_cover: int = typer.Option(
        100, "--cloud-cover", help="Maximum allowed cloud cover percentage."
    ),
    no_confirmation: bool = typer.Option(
        False,
        "--no-confirmation",
        help="Do not ask for confirmation before downloading",
    ),
    export: cli_options.ExportMetadataOptions = typer.Option(
        cli_options.ExportMetadataOptions.DISABLED.value,
        help="Export query results. Output can be used for editing and "
        "re-importing with the import command. If PIPE is chosen, the "
        "logger will be disabled and the output will be printed to "
        "stdout.",
        case_sensitive=False,
    ),
    results_only: bool = typer.Option(
        False,
        help="Only export the results of the query, do not download. "
        "This is useful for exporting the results of a query to a "
        "GeoJSON file and exiting the program without user input.",
    ),
    parallel: bool = typer.Option(
        True, help="Download all results in parallel"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing files in the output directory",
    ),
) -> None:
    """Batch download of satellite data with minimal user input"""

    # Setup the file logger
    core.logging.setup_file_logger(output_dir)

    # Disable the console logger if the user wants to pipe the output
    if export == cli_options.ExportMetadataOptions.PIPE.value:
        logging.getLogger().removeHandler(console_handler)

    query_results = core.query.batch_query(
        start=start,
        end=end,
        satellites=satellites,
        roi=roi,
        buffer=buffer,
        output_dir=output_dir,
        cloud_cover=cloud_cover,
        export=export,
        results_only=results_only,
    )
    # Sum results from all query results
    total_qty = sum([len(res) for sat, res in query_results])

    logger.info(f"Total (all satellites) results qty: {total_qty}")

    if total_qty == 0:
        sys.exit("Nothing to download")

    # Prompt user for confirmation before downloading
    if not no_confirmation:
        typer.confirm(
            "Do you want to download the results? (use --no-confirmation to "
            "skip this prompt)",
            abort=True,
        )

    core.utils.download(query_results, output_dir, parallel, overwrite)


@app.command()
def batch_interval(
    start: Annotated[
        datetime.datetime,
        typer.Option("--start", help="Start datetime of the search."),
    ],
    end: Annotated[
        datetime.datetime,
        typer.Option("--end", help="End datetime of the search."),
    ],
    satellites: Annotated[
        List[cli_options.SatelliteChoices],
        typer.Option(
            "--satellite",
            help="Satellite to consider. To add multiple satellites, "
            "use the option multiple times.",
            case_sensitive=False,
        ),
    ],
    roi: Annotated[  # Multichoice types are not possible yet, take a str
        str,  # then parse option in function
        typer.Option(  # https://github.com/tiangolo/typer/issues/140
            "--roi",
            help="Region of interest to consider. "
            "Format: <lon_min,lat_min,lon_max,lat_max> for boundary, "
            "<lon,lat> for a point, or path to a "
            "GeoJSON file (eg. <bounds.json>). All inputs are assumed to be "
            "projected in WGS84 (EPSG: 4326), and all point geometries must "
            "also use the buffer option.",
        ),
    ],
    frequency: Annotated[
        cli_options.TemporalFrequency,
        typer.Option(
            help="Frequency to download data at. "
            "Options: yearly, monthly, weekly, daily",
            case_sensitive=False,
        ),
    ],
    buffer: float = typer.Option(
        0.0, "--buffer", help="Buffer to apply to the ROI in metres."
    ),
    output_dir: str = typer.Option(
        core.config.constants.DEFAULT_DOWNLOAD_DIR,
        help="Output directory for the downloaded files.",
    ),
    cloud_cover: int = typer.Option(
        100, "--cloud-cover", help="Maximum allowed cloud cover percentage."
    ),
    no_confirmation: bool = typer.Option(
        False,
        "--no-confirmation",
        help="Do not ask for confirmation before downloading",
    ),
    export: cli_options.ExportMetadataOptions = typer.Option(
        cli_options.ExportMetadataOptions.DISABLED.value,
        help="Export query results. Output can be used for editing and "
        "re-importing with the import command. If PIPE is chosen, the "
        "logger will be disabled and the output will be printed to "
        "stdout.",
        case_sensitive=False,
    ),
    results_only: bool = typer.Option(
        False, help="Only export the results of the query, do not download"
    ),
    parallel: bool = typer.Option(
        True, help="Download all results in parallel"
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing files in the output directory",
    ),
) -> None:
    """Batch download with best cloud cover over a given time period

    Behaves similar to the batch command, but instead of downloading all
    results, it will download the result with the best cloud cover for each
    satellite:level combination over the given time period.

    For example, if the user specifies a time period of 2020-01-01 to
    2020-01-31, and the user specifies Sentinel-2 L1C and L2A, the command will

    """
    # Setup the file logger
    core.logging.setup_file_logger(output_dir)

    # Disable the console logger if the user wants to pipe the output
    if export == cli_options.ExportMetadataOptions.PIPE.value:
        logging.getLogger().removeHandler(console_handler)

    query_results = core.query.batch_query(
        start=start,
        end=end,
        satellites=satellites,
        roi=roi,
        buffer=buffer,
        output_dir=output_dir,
        cloud_cover=cloud_cover,
        export=export,
        results_only=results_only,
        interval_frequency=frequency,
    )
    # Sum results from all query results
    total_qty = sum([len(res) for sat, res in query_results])

    logger.info(f"Total (all satellites) results qty: {total_qty}")

    if total_qty == 0:
        sys.exit("Nothing to download")

    # Prompt user for confirmation before downloading
    if not no_confirmation:
        typer.confirm(
            "Do you want to download the results? (use --no-confirmation to "
            "skip this prompt)",
            abort=True,
        )

    core.utils.download(query_results, output_dir, parallel, overwrite)


@app.command()
def credentials(
    delete: str = typer.Option(None, help="Value to delete"),
    set: bool = typer.Option(False, help="Set all credentials"),
    show_secrets: bool = typer.Option(
        False, help="Display values of saved secrets"
    ),
) -> None:
    """Management of service credential keys"""

    if set:
        logger.info(
            "Setting credentials. Press enter to accept default "
            "value given in brackets."
        )
        core.credentials.set_all_credentials()

    if delete:
        core.credentials.delete_credential(delete)

    core.credentials.show_credential_list(show_secret=show_secrets)


def version_cb(value: bool) -> None:
    """Prints the version number of earth-extractor

    Parameters
    ----------
    value : bool
        The value of the --version option
    """

    if value:  # Only run on when --version is set
        typer.echo(f"earth-extractor {__version__}")
        sys.exit()


@app.callback()
def menu(
    version: bool = typer.Option(
        False,
        "--version",
        help="Prints the version number of earth-extractor",
        callback=version_cb,
        is_eager=True,
    ),
):
    """EarthExtractor - A tool for downloading satellite data from various
    providers. It is designed to be simple to use, and to provide a consistent
    interface for downloading data from different providers.

    Use the --help option on a subcommand to see more information about it.
    """
    pass


def main() -> None:
    """The main function of the application

    Used by the poetry entrypoint.
    """

    app()


if __name__ == "__main__":
    main()
