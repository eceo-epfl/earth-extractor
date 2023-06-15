from enum import Enum
from pydantic import BaseModel, Field, root_validator


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


class ROI(BaseModel):
    ''' Defines the region of interest to be used for the search

    The region of interest is defined by a list of floats. The first two
    floats define the top left corner of the rectangle, and the last two
    floats define the bottom right corner of the rectangle. The coordinates
    are in the WGS84 coordinate system.
    '''

    # Limit latitude to -90 to 90
    latmin: float = Field(..., ge=-90, le=90)
    lonmin: float = Field(..., ge=-180, le=180)
    latmax: float = Field(..., ge=-90, le=90)
    lonmax: float = Field(..., ge=-180, le=180)

    @classmethod
    def from_string(cls, v: str):
        ''' Convert a string into a list of floats

        The string is split by a comma (',') and each element is converted
        into a float. The resulting list is returned.
        '''

        if isinstance(v, str):
            values = [float(x) for x in v.split(',')]

            return cls(
                latmin=values[0], lonmin=values[1],
                latmax=values[2], lonmax=values[3]
            )