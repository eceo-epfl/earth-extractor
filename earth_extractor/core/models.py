from pydantic import BaseModel, Field, AnyUrl
import shapely
from typing import Any, TYPE_CHECKING, Optional
from dataclasses import dataclass

if TYPE_CHECKING:
    from earth_extractor.satellites.enums import (
        ProcessingLevel, Sensor, Satellite
    )


class BBox(BaseModel):
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

    def __str__(self):
        return f"{self.latmin},{self.lonmin},{self.latmax},{self.lonmax}"

    def to_shapely(self):
        ''' Convert the ROI into a shapely object

        The shapely object is a rectangle defined by the top left and bottom
        right corners of the ROI.
        '''

        return shapely.geometry.box(
            self.lonmin, self.latmin, self.lonmax, self.latmax
        )


class Point(BaseModel):
    ''' Defines the point of interest to be used for the search '''

    # Limit latitude to -90 to 90
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)

    @classmethod
    def from_string(cls, v: str):
        ''' Convert a string into a list of floats

        The string is split by a comma (',') and each element is converted
        into a float. The resulting list is returned.
        '''

        if isinstance(v, str):
            values = [float(x) for x in v.split(',')]

            return cls(lat=values[0], lon=values[1])

    def __str__(self):
        return f"{self.lat},{self.lon}"

    def to_shapely(self):
        ''' Convert the ROI into a shapely object

        The shapely object is a rectangle defined by the top left and bottom
        right corners of the ROI.
        '''

        return shapely.geometry.Point(self.lon, self.lat)


@dataclass
class CommonSearchResult:
    ''' A class to support the exchange of search results between providers

    This class is used to standardise the search results between providers
    such that the the Provider/Satellite classes can be agnostic to the
    provider of the search results.
    '''

    product_id: Optional[Any] = None
    link: Optional[AnyUrl] = None
    identifier: Optional[str] = None
    filename: Optional[str] = None

    cloud_cover_percentage: Optional[float] = None
    size: Optional[float] = None

    processing_level: Optional["ProcessingLevel"] = None
    sensor: Optional["Sensor"] = None
    satellite: Optional["Satellite"] = None

    geometry: Optional[str] = None
