from earth_extractor.satellites.base import Satellite
from earth_extractor.satellites import enums
from earth_extractor.providers import nasa_cmr
from earth_extractor import core
import logging

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

""" Define the MODIS constellation """

modis_terra: Satellite = Satellite(
    query_provider=nasa_cmr,
    download_provider=nasa_cmr,
    name=enums.Satellite.MODIS_TERRA,
    description="Sentinel 1",
    processing_levels=[enums.ProcessingLevel.L1B],
    sensors=[enums.Sensor.MODIS],
    filters=[],
)

modis_aqua: Satellite = Satellite(
    query_provider=nasa_cmr,
    download_provider=nasa_cmr,
    name=enums.Satellite.MODIS_AQUA,
    description="Sentinel 1",
    processing_levels=[enums.ProcessingLevel.L1B],
    sensors=[enums.Sensor.MODIS],
    filters=[],
)
