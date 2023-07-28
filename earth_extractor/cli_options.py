from enum import Enum
from earth_extractor.satellites import sentinel, modis, viirs, swissimage


class SatelliteChoices(str, Enum):
    # Sentinel
    SENTINEL1L1 = "SENTINEL1:L1"
    SENTINEL2L1C = "SENTINEL2:L1C"
    SENTINEL2L2A = "SENTINEL2:L2A"
    SENTINEL3L1 = "SENTINEL3:L1"
    SENTINEL3L2 = "SENTINEL3:L2"

    # MODIS
    MODISTERRA = "MODIS_TERRA:L1B"
    MODISAQUA = "MODIS_AQUA:L1B"

    # VIIRS
    VIIRS = "VIIRS:L1"

    # SwissImage
    SWISSIMAGE10CM = "SWISSIMAGE:CM10"
    SWISSIMAGE200CM = "SWISSIMAGE:CM200"


class Satellites(Enum):
    SENTINEL1 = sentinel.sentinel_1
    SENTINEL2 = sentinel.sentinel_2
    SENTINEL3 = sentinel.sentinel_3
    MODIS_TERRA = modis.modis_terra
    MODIS_AQUA = modis.modis_aqua
    VIIRS = viirs.viirs
    SWISSIMAGE = swissimage.swissimage


class TemporalFrequency(str, Enum):
    """Enum for temporal frequency to be used for

    In reverse as Typer only uses values and not names for selection in CLI
    """

    D = "DAILY"
    W = "WEEKLY"
    M = "MONTHLY"
    Y = "YEARLY"


class ExportMetadataOptions(str, Enum):
    DISABLED = "DISABLED"
    FILE = "FILE"
    PIPE = "PIPE"
