from earth_extractor.providers import Provider
import logging
from earth_extractor.satellites import enums
from earth_extractor import core


logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


nasa_cmr: Provider = Provider(
    name="CMR",
    description="Common Metadata Repository",
    satellites={enums.Satellite.SENTINEL3: ''},
    uri="https://cmr.earthdata.nasa.gov"
)
