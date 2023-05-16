from enum import Enum


class Satellites(str, Enum):
    SENTINEL1_L1 = "SENTINEL1:L1"
    SENTINEL1_L2 = "SENTINEL1:L2"
    SENTINEL2_L1 = "SENTINEL2:L1"
    SENTINEL2_L2 = "SENTINEL2:L2"
    sentinel3 = "sentinel3:L1"


class Levels(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
