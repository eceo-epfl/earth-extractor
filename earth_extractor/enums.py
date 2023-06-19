from enum import Enum
from pydantic import BaseModel, Field


class Satellite(str, Enum):
    ''' Contains the supported satellites and levels supported by the library

    As the constraint of each level is dependent on the satellite, the
    satellite and level are combined into a single string, separated by a colon
    (':'). For example SENTINEL1:L1 is L1 of the Sentinel 1.
    '''
    SENTINEL1 = "SENTINEL1"
    SENTINEL2 = "SENTINEL2"
    SENTINEL3 = "SENTINEL3"


class ProcessingLevel(str, Enum):
    ''' Satellite processing levels
    As defined by:
    https://www.earthdata.nasa.gov/engage/open-data-services-and-software/data-information-policy/data-levels
    '''

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


class Sensor(str, Enum):
    MSI = "MSI"
    C_SAR = "C-SAR"
    OLCI = "OLCI"
    SLSTR = "SLSTR"
    SRAL = "SRAL"
