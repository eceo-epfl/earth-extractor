from earth_extractor.providers import Provider
import logging
from earth_extractor.satellites import enums

logger = logging.getLogger(__name__)


nasa_cmr: Provider = Provider(
    name="CMR",
    description="Common Metadata Repository",
    satellites={enums.Satellite.SENTINEL3: ''},
    uri="https://cmr.earthdata.nasa.gov"
)
