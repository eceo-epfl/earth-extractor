from earth_extractor.satellites import sentinel_1
from earth_extractor.providers import Provider
import logging


logger = logging.getLogger(__name__)


asf = Provider(
    name="Alaskan Satellite Facility",
    description="Alaskan Satellite Facility",
    satellites=[(sentinel_1, '')],
    uri="https://asf.alaska.edu"
)
