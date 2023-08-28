from enum import Enum


class ProcessingLevel(str, Enum):
    """Satellite processing levels
    As defined by:
    https://www.earthdata.nasa.gov/engage/open-data-services-and-software/data-information-policy/data-levels
    """

    L0 = "L0"
    L1 = "L1"
    L1A = "L1A"
    L1B = "L1B"
    L1C = "L1C"
    L2 = "L2"
    L2A = "L2A"
    L2B = "L2B"
    L3 = "L3"
    L3A = "L3A"
    L4 = "L4"

    # Spatial Resolutions (breaks the naming convention unfortunately ...)
    # SWISSIMAGE is provided in two products, 0.1m and 2m
    # Perhaps reassess naming of "ProcessingLevel" to something else later if
    # resolutions in Satellite clases are to be added
    CM10 = "CM10"
    CM200 = "CM200"


class Sensor(str, Enum):
    MSI = "MSI"
    C_SAR = "C-SAR"
    OLCI = "OLCI"
    SLSTR = "SLSTR"
    SRAL = "SRAL"
    MODIS = "MODIS"
    VIIRS = "VIIRS"
    SWISSIMAGE = "SWISSIMAGE"


class Satellite(Enum):
    """Contains the supported satellites supported by the library"""

    SENTINEL1 = "SENTINEL1"
    SENTINEL2 = "SENTINEL2"
    SENTINEL3 = "SENTINEL3"
    MODIS_TERRA = "MODIS_TERRA"
    MODIS_AQUA = "MODIS_AQUA"
    VIIRS = "VIIRS"
    SWISSIMAGE = "SWISSIMAGE_10CM"


class Filters(Enum):
    """The available filters for the satellites

    To understand the filtering capabilities for each sensor, for example
    radar satellites do not have a cloud cover percentage, so manage those that
    do have it.
    """

    CLOUD_COVER = "CLOUD_COVER"
