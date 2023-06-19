from earth_extractor.satellites import sentinel_2
from earth_extractor.providers import Provider
import logging

logger = logging.getLogger(__name__)


sinergise = Provider(
    name="Sinergise",
    description="Sinergise",
    satellites=[(sentinel_2, '')],
    uri="https://www.sinergise.com"
)
