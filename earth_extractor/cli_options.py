from enum import Enum
from earth_extractor import satellites
from earth_extractor.satellites.base import Satellite


class SatelliteChoices(str, Enum):
    SENTINEL1L1 = "SENTINEL1:L1"
    SENTINEL1L2 = "SENTINEL1:L2"

    SENTINEL2L1C = "SENTINEL2:L1C"
    SENTINEL2L2A = "SENTINEL2:L2A"

    SENTINEL3L1 = "SENTINEL3:L1"
    SENTINEL3L2 = "SENTINEL3:L2"


class Satellites(Enum):
    SENTINEL1 = satellites.sentinel.sentinel_1
    SENTINEL2 = satellites.sentinel.sentinel_2
    SENTINEL3 = satellites.sentinel.sentinel_3
