#!/usr/bin/env python3
import eodag
import typer
from typing import Annotated, Optional, List
from enum import Enum



class Satellites(str, Enum):
    sentinel1 = "sentinel1"
    sentinel2 = "sentinel2"
    sentinel3 = "sentinel3"


# Initialise the Typer class
app = typer.Typer(no_args_is_help=True)



# @app.command()
# def main(textstring):
#     print(textstring)
# def main(dag: eodag.EODataAccessGateway):


#     search_results, _ = dag.search(
#         productType="S2_MSI_L1C",
#         start="2021-03-01",
#         end="2021-03-31",
#         geom={"lonmin": 1, "latmin": 43, "lonmax": 2, "latmax": 44}
#     )
#     product_paths = dag.download_all(search_results)

#     return product_paths


@app.command()
def show_providers(
    satellites: Annotated[
        List[Satellites],
        typer.Option("--add-satellite", help="Satellites to download from.")
    ] = [Satellites.sentinel1, Satellites.sentinel2, Satellites.sentinel3]
) -> None:
    dag = eodag.EODataAccessGateway()
    print(satellites)
    return
    for product in dag.list_product_types():
        # print(product['ID'])
        product_providers = dag.available_providers(product['ID'])

        # print(product_providers)
        if (
            'scihub' in product_providers
            and product['platform'].lower() in satellites
        ):
            print(f"ID: {product['ID']} providers: {product_providers}")
            exclude_keys = ['abstract', 'license', 'missionStartDate']

            # Exclude keys from print
            new_d = {
                k: product[k] for k
                in set(list(product.keys())) - set(exclude_keys)
            }
            print(new_d)
            print()


if __name__ == "__main__":
    app()
    # print(main())
    # dag = eodag.EODataAccessGateway()

    # data_types = dag.list_product_types()
    # data_types = [(x['ID'], x['platform'], x['keywords']) for x in dag.list_product_types() if x['platform'] and 'sentinel' in x['platform'].lower()]
    # for dtype in data_types:
        # print(dtype)
        # if 'sentinel'dtype[1]
