from earth_extractor.satellites import sentinel_3
from earth_extractor.providers import Provider
import logging

logger = logging.getLogger(__name__)


nasa_cmr = Provider(
    name="CMR",
    description="Common Metadata Repository",
    satellites=[(sentinel_3, '')],
    uri="https://cmr.earthdata.nasa.gov"
)
