from enum import Enum


class Satellites(str, Enum):
    ''' Contains the supported satellites and levels supported by the library

    As the constraint of each level is dependent on the satellite, the
    satellite and level are combined into a single string, separated by a colon
    (':'). For example SENTINEL1:L1 is L1 of the Sentinel 1.
    '''

    SENTINEL1_L1 = "SENTINEL1:L1"
    SENTINEL1_L2 = "SENTINEL1:L2"

    # Sentinel 2
    SENTINEL2_L1 = "SENTINEL2:L1"
    SENTINEL2_L2 = "SENTINEL2:L2"

    # Sentinel 3
    SENTINEL3_L1 = "SENTINEL3:L1"
