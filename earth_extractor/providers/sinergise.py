
from earth_extractor.providers import Provider
from earth_extractor.core.credentials import get_credentials
from earth_extractor.core.models import BBox
from typing import Any, List, TYPE_CHECKING
from sentinelhub import DataCollection, SHConfig, SentinelHubCatalog
import logging
import datetime
from earth_extractor.satellites import enums

if TYPE_CHECKING:
    from earth_extractor.satellites.base import Satellite

logger = logging.getLogger(__name__)

credentials = get_credentials()


class SinergiseSentinelHub(Provider):
    def query(
        self,
        satellite: "Satellite",
        processing_level: enums.ProcessingLevel,
        roi: BBox,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: int | None = None,
    ) -> List[Any]:

        logger.info("Querying Sinergise Sentinel Hub")
        if (
            credentials.SINERGISE_CLIENT_SECRET
            or credentials.SINERGISE_CLIENT_ID
        ) is None:
            raise ValueError(
                "Sinergise Sentinel Hub credentials not found. "
                "Please set SINERGISE_CLIENT_SECRET and SINERGISE_CLIENT_ID "
                "in the config file."
            )

        config = SHConfig(
            credentials.SINERGISE_CLIENT_ID,
            credentials.SINERGISE_CLIENT_SECRET
        )
        catalog = SentinelHubCatalog(config=config)

        if satellite.name not in self.satellites:
            raise ValueError(
                f"Satellite {satellite.name} not supported by Copernicus "
                f"Open Access Hub. Available satellites: {self.satellites}"
            )

        logger.info(f"Satellite: {satellite.name} "
                    f"({self.satellites[satellite.name]}"
                    f"{processing_level.value}")

        product_type = self.products.get(
            (satellite.name, processing_level), None
        )
        if not product_type:
            raise ValueError(
                f"Processing level {processing_level.value} not supported "
                f"by Copernicus Open Access Hub for satellite "
                f"{satellite.name}. Available processing levels: "
                f"{self.products}"
            )

        raise NotImplementedError("Sinergise Sentinel Hub not implemented")
        # catalog.get_feature(product_type, )
        # products = api.query(
        #     roi.to_wkt(),
        #     platformname=self.satellites[satellite.name],
        #     # producttype=product_type,
        #     # processinglevel=processing_level.value,
        #     cloudcoverpercentage=(0, cloud_cover) if cloud_cover else None,
        #     date=(start_date, end_date),
        # )

        # return products


sinergise: SinergiseSentinelHub = SinergiseSentinelHub(
    name="Sinergise",
    description="Sinergise Sentinel Hub",
    satellites={enums.Satellite.SENTINEL2: ''},
    uri="https://www.sinergise.com",
    products={
        (enums.Satellite.SENTINEL2,
         enums.ProcessingLevel.L1C): DataCollection.SENTINEL2_L1C,
        (enums.Satellite.SENTINEL2,
         enums.ProcessingLevel.L2A): DataCollection.SENTINEL2_L2A,
    }
)
