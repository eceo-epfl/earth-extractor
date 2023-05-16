#!/usr/bin/env python3
import eodag
import typer
from typing import Annotated, Optional, List, Tuple
from earth_explorer.enums import Satellites, Levels

# Initialise the Typer class
app = typer.Typer(no_args_is_help=True)


@app.command()
def show_providers(
    satellites: Annotated[
        List[Satellites],
        typer.Option("--satellite",
                     help="Satellite and its layer to consider.")
    ] = [Satellites.SENTINEL1_L1],
) -> None:
    dag = eodag.EODataAccessGateway()
    print(satellites)

    # Rearrange the Satellite:Level structure into tuples
    satellite_level_choices = []
    for satellite in satellites:
        sat, level = satellite.split(':')
        satellite_level_choices.append((sat, level))

    print(satellite_level_choices)
    # return
    product_list = []
    for product in dag.list_product_types():
        # print(product['ID'])
        product_providers = dag.available_providers(product['ID'])

        # print(product_providers)
        if (
            'scihub' in product_providers
            and (
                (product['platform'], product['processingLevel'])
                in satellite_level_choices)
            # and product['platform'].lower() in satellites
            # and product['processingLevel'] in levels
        ):
            print(f"ID: {product['ID']}", end=' ')
            exclude_keys = ['abstract', 'license', 'missionStartDate']

            # Exclude keys from print
            new_d = {
                k: product[k] for k
                in set(list(product.keys())) - set(exclude_keys)
            }
            print(new_d)
            print()
            product_list.append(product['ID'])

    print(product_list)



if __name__ == "__main__":
    app()
    # print(main())
    # dag = eodag.EODataAccessGateway()

    # data_types = dag.list_product_types()
    # data_types = [(x['ID'], x['platform'], x['keywords']) for x in dag.list_product_types() if x['platform'] and 'sentinel' in x['platform'].lower()]
    # for dtype in data_types:
        # print(dtype)
        # if 'sentinel'dtype[1]
