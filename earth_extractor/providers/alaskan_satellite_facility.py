from earth_extractor.providers import Provider
from earth_extractor.satellites import enums
import logging


logger = logging.getLogger(__name__)


asf: Provider = Provider(
    name="Alaskan Satellite Facility",
    description="Alaskan Satellite Facility",
    satellites=[(enums.Satellite.SENTINEL1, '')],
    uri="https://asf.alaska.edu"
)
