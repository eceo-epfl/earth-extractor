from earth_extractor.classes import Provider, Satellite
from earth_extractor.satellites import sentinel_1, sentinel_2, sentinel_3
from earth_extractor.config import credentials
from earth_extractor.models import ROI
from typing import Any, Dict, List
from sentinelsat import SentinelAPI
import logging
import datetime
logger = logging.getLogger(__name__)


class CopernicusOpenAccessHub(Provider):
    def __init__(self) -> None:
        self.name: str = "scihub"
        self.description: str = "Copernicus Open Access Hub"
        self.uri: str = "https://scihub.copernicus.eu"
        self.satellites: Dict[Satellite, str] = {
            sentinel_1: "Sentinel-1",
            sentinel_2: "Sentinel-2",
            sentinel_3: "Sentinel-3",
        }

    def query(
        self,
        satellite: Satellite,
        roi: ROI,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cloud_cover: int = 100,
    ) -> List[Any]:

        logger.info("Querying Copernicus Open Access Hub")
        api = SentinelAPI(credentials.SCIHUB_USERNAME,
                          credentials.SCIHUB_PASSWORD)

        if satellite not in self.satellites:
            raise ValueError(
                "Satellite not supported by Copernicus Open Access Hub"
            )

        products = api.query(
            roi.to_wkt(),
            platformname=self.satellites[satellite],
            cloudcoverpercentage=(0, cloud_cover),
            date=(start_date, end_date),
        )

        return products
