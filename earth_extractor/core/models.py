from pydantic import BaseModel, Field, AnyUrl
import shapely
from typing import Any
from earth_extractor.satellites.enums import ProcessingLevel, Sensor, Satellite


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

    @classmethod
    def from_tuple(cls, v: str):
        ''' Convert a tuple into the ROI model

        The order of the tuple is (latmin, lonmin, latmax, lonmax).
        '''

        if isinstance(v, tuple):
            return cls(
                latmin=v[0], lonmin=v[1],
                latmax=v[2], lonmax=v[3]
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

    def to_wkt(self):
        ''' Convert the ROI into a WKT string

        The WKT string is a rectangle defined by the top left and bottom
        right corners of the ROI.
        '''

        return self.to_shapely().wkt


class CommonSearchResult(BaseModel):
    ''' A class to encompass the exchange of search results between providers

    This class is used to standardise the search results between providers
    such that the the Provider/Satellite classes can be agnostic to the
    provider of the search results.
    '''

    hash: Any | None = None
    link: AnyUrl | None = None
    identifier: str | None = None
    filename: str | None = None

    cloud_cover_percentage: float | None = None
    size_mb: float | None = None

    processing_level: ProcessingLevel | None = None
    sensor: Sensor | None = None
    satellite: Satellite | None = None

    class Config:
        extra = "allow"  # Allow extra fields to be added to the model
