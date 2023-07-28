from earth_extractor.satellites.base import Satellite
from earth_extractor.satellites import enums
from earth_extractor.providers import nasa_cmr
from earth_extractor import core
import logging

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

""" Define the VIIRS constellation """

viirs: Satellite = Satellite(
    query_provider=nasa_cmr,
    download_provider=nasa_cmr,
    name=enums.Satellite.VIIRS,
    description="Visible Infrared Imaging Radiometer Suite",
    processing_levels=[enums.ProcessingLevel.L1],
    sensors=[enums.Sensor.VIIRS],
    filters=[],
)
