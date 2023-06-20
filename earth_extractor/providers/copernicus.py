from earth_extractor.providers import Provider
from earth_extractor.satellites import enums
from earth_extractor.config import credentials
from earth_extractor.models import ROI
from typing import Any, List, TYPE_CHECKING
from sentinelsat import SentinelAPI
import logging
import datetime

if TYPE_CHECKING:
    from earth_extractor.satellites.base import Satellite

logger = logging.getLogger(__name__)


class CopernicusOpenAccessHub(Provider):
    def query(
        self,
        satellite: "Satellite",
        roi: ROI,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: int = 100,
    ) -> List[Any]:

        logger.info("Querying Copernicus Open Access Hub")
        api = SentinelAPI(
            credentials.SCIHUB_USERNAME, credentials.SCIHUB_PASSWORD
        )

        if satellite not in self.satellites:
            raise ValueError(
                "Satellite not supported by Copernicus Open Access Hub"
            )

        products = api.query(
            roi.to_wkt(),
            platformname=self.satellites[satellite.name],
            cloudcoverpercentage=(0, cloud_cover),
            date=(start_date, end_date),
        )

        return products


copernicus_scihub: CopernicusOpenAccessHub = CopernicusOpenAccessHub(
    name="scihub",
    description="Copernicus Open Access Hub",
    uri="https://scihub.copernicus.eu",
    satellites={
        enums.Satellite.SENTINEL1: "Sentinel-1",
        enums.Satellite.SENTINEL2: "Sentinel-2",
        enums.Satellite.SENTINEL3: "Sentinel-3",
    }
)
