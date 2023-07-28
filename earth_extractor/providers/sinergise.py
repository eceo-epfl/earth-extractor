from earth_extractor.providers import Provider
from earth_extractor import core
from typing import Any, List, TYPE_CHECKING
from sentinelhub import DataCollection, SHConfig, SentinelHubCatalog
import logging
import datetime
from earth_extractor.satellites import enums

if TYPE_CHECKING:
    from earth_extractor.satellites.base import Satellite

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

credentials = core.credentials.get_credentials()


class SinergiseSentinelHub(Provider):
    def query(
        self,
        satellite: "Satellite",
        processing_level: enums.ProcessingLevel,
        roi: core.models.BBox,
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
            credentials.SINERGISE_CLIENT_SECRET,
        )
        catalog = SentinelHubCatalog(config=config)

        logger.info(
            f"Satellite: {satellite.name} ({satellite.name}) "
            f"{processing_level.value}"
        )

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


sinergise: SinergiseSentinelHub = SinergiseSentinelHub(
    name="Sinergise",
    description="Sinergise Sentinel Hub",
    uri="https://www.sinergise.com",
    products={
        (enums.Satellite.SENTINEL2, enums.ProcessingLevel.L1C): [
            DataCollection.SENTINEL2_L1C
        ],
        (enums.Satellite.SENTINEL2, enums.ProcessingLevel.L2A): [
            DataCollection.SENTINEL2_L2A
        ],
    },
)
