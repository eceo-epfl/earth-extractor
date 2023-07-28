from earth_extractor.satellites.base import Satellite
from earth_extractor.satellites import enums
from earth_extractor.providers import swiss_topo
from earth_extractor import core
import logging

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


swissimage: Satellite = Satellite(
    query_provider=swiss_topo,
    download_provider=swiss_topo,
    name=enums.Satellite.SWISSIMAGE,
    description="SwissImage 10cm",
    processing_levels=[
        enums.ProcessingLevel.CM10,
        enums.ProcessingLevel.CM200,
    ],
    sensors=[],
    filters=[],
)
