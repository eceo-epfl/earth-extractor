from earth_extractor.satellites.base import Satellite
from earth_extractor.satellites import enums
from earth_extractor.providers import copernicus_scihub, asf
from earth_extractor import core
import logging

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

""" Define the Sentinel satellites

    The satellites are defined as instances of the Satellite class.
"""

sentinel_1: Satellite = Satellite(
    query_provider=copernicus_scihub,
    download_provider=asf,
    name=enums.Satellite.SENTINEL1,
    description="Sentinel 1",
    processing_levels=[enums.ProcessingLevel.L1, enums.ProcessingLevel.L2],
    sensors=[enums.Sensor.C_SAR],
    filters=[],
)

sentinel_2: Satellite = Satellite(
    query_provider=copernicus_scihub,
    download_provider=copernicus_scihub,
    name=enums.Satellite.SENTINEL2,
    description="Sentinel 2",
    processing_levels=[enums.ProcessingLevel.L1C, enums.ProcessingLevel.L2A],
    sensors=[enums.Sensor.MSI],
    filters=[enums.Filters.CLOUD_COVER],
)

sentinel_3: Satellite = Satellite(
    query_provider=copernicus_scihub,
    download_provider=copernicus_scihub,
    name=enums.Satellite.SENTINEL3,
    description="Sentinel 3",
    processing_levels=[enums.ProcessingLevel.L1, enums.ProcessingLevel.L2],
    sensors=[enums.Sensor.OLCI, enums.Sensor.SLSTR, enums.Sensor.SRAL],
    filters=[enums.Filters.CLOUD_COVER],
)
