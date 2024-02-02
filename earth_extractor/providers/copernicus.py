from earth_extractor.providers import Provider
from earth_extractor.core.credentials import get_credentials
from earth_extractor.core.models import CommonSearchResult
from typing import Any, List, TYPE_CHECKING, Dict, Optional
import logging
import datetime
import shapely
import shapely.geometry
from shapely import wkt
from earth_extractor.satellites import enums
from earth_extractor import core
import requests
from earth_extractor.core.config import constants

if TYPE_CHECKING:
    from earth_extractor.satellites.base import Satellite

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

credentials = get_credentials()


class CopernicusDataSpace(Provider):
    def get_access_token(
        self: "CopernicusDataSpace",
        username: str | None,
        password: str | None,
        client_id: str = constants.COPERNICUS_APPLICATION_ID,
    ) -> str:

        if username is None or password is None:
            raise ValueError(
                "Username and password are required to get an access token"
            )
        data = {
            "client_id": client_id,  # Set unique id for this application
            "username": username,
            "password": password,
            "grant_type": "password",
        }
        try:
            r = requests.post(
                "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
                "protocol/openid-connect/token",
                data=data,
            )
            r.raise_for_status()
        except Exception as e:
            raise Exception(
                "Access token creation failed. Exception raised from the "
                f"server was: {e}"
            )
        return r.json()["access_token"]

    def query(
        self,
        satellite: "Satellite",
        processing_level: enums.ProcessingLevel,
        roi: shapely.geometry.base.BaseGeometry,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: Optional[int] = None,
    ) -> List[Dict[Any, Any]]:
        """Query the Copernicus Data Space for data

        No credentials are required to query
        """

        # If cloud cover percentage is 100, set to None for API
        if cloud_cover is None:
            cloud_cover = 100

        # Variable to combine all CommonSearchResult objects into one
        all_products = []

        for product_type in self.products.get(
            (satellite.name, processing_level), []
        ):
            # We do a list here because in some cases, a satellite may have
            # multiple product types for a given processing level (sentinel 3
            # has two product types for L2)
            logger.info(f"Product type: {product_type}")
            if not product_type:
                raise ValueError(
                    f"Processing level {processing_level.value} not supported "
                    f"by Copernicus Data Space for satellite "
                    f"{satellite.name}. Available processing levels: "
                    f"{self.products}"
                )

            # Build the query URL
            base_url = (
                "https://catalogue.dataspace.copernicus.eu/odata/v1/"
                "Products?$filter="
            )
            query_elements = []
            try:
                if cloud_cover and cloud_cover < 100:
                    query_elements.append(
                        f"Attributes/OData.CSC.DoubleAttribute/"
                        "any(att:att/Name eq 'cloudCover' "
                        "and att/OData.CSC.DoubleAttribute/Value"
                        f" le {cloud_cover:.2f})"
                    )
                if roi:
                    query_elements.append(
                        "OData.CSC.Intersects("
                        f"area=geography'SRID=4326;{roi.wkt}')"
                    )
                query_elements.append(
                    f"Attributes/OData.CSC.StringAttribute/"
                    "any(att:att/Name eq 'productType' "
                    "and att/OData.CSC.StringAttribute/Value eq "
                    f"'{product_type}')"
                )
                query_elements.append(
                    f"ContentDate/Start gt {start_date.isoformat()}.000Z"
                )
                query_elements.append(
                    f"ContentDate/Start lt {end_date.isoformat()}.000Z"
                )

                query_url = (
                    f"{base_url}{' and '.join(query_elements)}"
                    "&$expand=Assets&$expand=Attributes&$top=1000"
                )

                # Query the API
                products = requests.get(query_url).json()

                # Translate the results to a common format
                all_products += self.translate_search_results(products)
                count = 1

                next_page = products.get("@odata.nextLink", None)
                while next_page:
                    products = requests.get(next_page).json()
                    all_products += self.translate_search_results(products)
                    next_page = products.get("@odata.nextLink", None)
                    count += 1
                    logger.info(f"Querying page {count}")

            except Exception as e:
                logger.error(f"Authentication error: {e}")
                return []

        return all_products

    def download_many(
        self,
        search_results: List[CommonSearchResult],
        download_dir: str,
        overwrite: bool = False,
        processes: int = constants.PARRALLEL_PROCESSES_DEFAULT,
    ) -> None:
        """Using the search results from query(), download the data

        Parameters
        ----------
        search_results : List[str]
            The search results
        download_dir : str
            The directory to download the data to
        overwrite : bool, optional
            Whether to overwrite existing files, by default False
        processes : int, optional
            The number of processes to use for downloading

        Returns
        -------
        None
        """

        # Convert the search results to a list of URIs

        # Check that the provider's credentials that are needed are set
        self._check_credentials_exist()

        try:
            access_token = self.get_access_token(
                credentials.COPERNICUS_USERNAME,
                credentials.COPERNICUS_PASSWORD,
            )
        except Exception as e:
            raise ValueError(
                f"Copernicus Data Space access token creation failed: {e}"
            )

        urls = [str(x.url) for x in search_results if x.url]

        auth_header = {"Authorization": f"Bearer {access_token}"}

        for url in urls:
            try:
                core.utils.download_parallel(
                    urls, download_dir, auth_header, overwrite, processes
                )
            except RuntimeError as e:
                # Log the exception and continue to the next file
                logger.error(e)
                continue

    def translate_search_results(
        self, provider_search_results: Dict[Any, Any]
    ) -> List[CommonSearchResult]:
        """Translate search results from a provider to a common format

        Parameters
        ----------
        provider_search_results : Dict[Any, Any]
            The search results from the provider

            Returns
            -------
            List[CommonSearchResult]
                The search results in a common format
        """

        common_results = []

        for props in provider_search_results["value"]:
            # Get the satellite and processing level from reversed mapping of
            # the provider's "products" dictionary
            sat, level = None, None
            for odata_props in props["Attributes"]:
                if odata_props["Name"] == "productType":
                    sat, level = self._products_reversed[odata_props["Value"]]

            if sat is None or level is None:
                logger.warn(
                    "Satellite and processing level could not be determined "
                    "from the search results"
                )
                continue

            # Geometry is encoded with SRID, split, remove trailing apostrophe
            wkt_geometry = props.get("Footprint").split(";")[-1][:-1]
            geometry_shapely = wkt.loads(wkt_geometry)

            url = (
                "https://zipper.dataspace.copernicus.eu/odata/v1/"
                f"Products({props.get('Id')})/$value"
            )
            common_results.append(
                CommonSearchResult(
                    geometry=geometry_shapely,
                    product_id=props.get("Id"),
                    link=props.get("S3Path"),
                    url=url,
                    identifier=props.get("Id"),
                    filename=props.get("Name"),
                    size=props.get("ContentLength"),
                    time=datetime.datetime.strptime(
                        props.get("OriginDate"), "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),
                    processing_level=level,
                    satellite=sat,
                )
            )
            print(common_results[0].time)
        return common_results


copernicus_dataspace: CopernicusDataSpace = CopernicusDataSpace(
    name="scihub",
    description="Copernicus Data Space",
    uri="https://dataspace.copernicus.eu",
    products={
        (enums.Satellite.SENTINEL1, enums.ProcessingLevel.L1): ["IW_GRDH_1S"],
        (enums.Satellite.SENTINEL2, enums.ProcessingLevel.L1C): ["S2MSI1C"],
        (enums.Satellite.SENTINEL2, enums.ProcessingLevel.L2A): ["S2MSI2A"],
        (enums.Satellite.SENTINEL3, enums.ProcessingLevel.L1): ["OL_1_EFR___"],
        (enums.Satellite.SENTINEL3, enums.ProcessingLevel.L2): [
            "OL_2_LFR___",
            "OL_2_WFR___",
        ],
    },
    credentials_required=["COPERNICUS_USERNAME", "COPERNICUS_PASSWORD"],
)
