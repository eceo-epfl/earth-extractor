#!/usr/bin/env python3
import eodag
import datetime
import typer
from typing import Annotated, List
from enums import Satellite, ProcessingLevel, ROI
import logging
from earth_extractor.config import constants

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
                     help="Satellite and its layer to consider.")
    ],
    level: Annotated[
        List[ProcessingLevel],
        typer.Option("--level",
                     help="Processing level to consider.")
    ],
    no_confirmation: bool = typer.Option(
        False, "--no-confirmation",
        help="Do not ask for confirmation before downloading"
    )
) -> None:
    dag = eodag.EODataAccessGateway()
    # dag.set_preferred_provider("peps")
    # Convert the ROI string into a list of floats
    # roi: List[float] = [float(x) for x in roi.split(',')]

    roi = ROI.from_string(roi)

    # Rearrange the Satellite:Level structure into tuples
    satellite_level_choices: List[str] = []
    # for satellite in satellites:
        # sat, level = satellite.split(':')
        # satellite_level_choices.append((sat, level))

    print(satellite_level_choices)
    product_list = []
    for product in dag.list_product_types():
        # print(product['ID'])
        product_providers = dag.available_providers(product['ID'])

        # print(product_providers)
        if (product['platform'] in satellites) and (product['processingLevel'] in level):
            # (product['platform'], product['processingLevel'])
            # in satellite_level_choices
            # and product['platform'].lower() in satellites
            # and product['processingLevel'] in levels
        # ):
            print(f"ID: {product['ID']}", end=' ')
            exclude_keys = ['abstract', 'license', 'missionStartDate']

            # Exclude keys from print
            new_d = {
                k: product[k] for k
                in set(list(product.keys())) - set(exclude_keys)
            }
            # print(new_d)
            # print(json.dumps(new_d, indent=4))
            # print(new_d['processingLevel'])
            print()
            product_list.append(product['ID'])

    logger.info(f"ROI: {roi}")
    logger.info(f"Time: {start} {end}")
    logger.info(product_list)

    results = []
    # Search for each satellite and level and combine results
    for product_id in product_list:
        res = dag.search_all(start=start.isoformat(), end=end.isoformat(),
                             geom=roi.dict(), productType=product_id)
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
    [logger.info(path) for path in paths]


if __name__ == "__main__":
    app()
    # print(main())
    # dag = eodag.EODataAccessGateway()

    # data_types = dag.list_product_types()
    # data_types = [(x['ID'], x['platform'], x['keywords']) for x in dag.list_product_types() if x['platform'] and 'sentinel' in x['platform'].lower()]
    # for dtype in data_types:
        # print(dtype)
        # if 'sentinel'dtype[1]
