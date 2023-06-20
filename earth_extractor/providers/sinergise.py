from earth_extractor.providers import Provider
import logging
from earth_extractor.satellites import enums

logger = logging.getLogger(__name__)


sinergise: Provider = Provider(
    name="Sinergise",
    description="Sinergise",
    satellites={enums.Satellite.SENTINEL2: ''},
    uri="https://www.sinergise.com"
)
