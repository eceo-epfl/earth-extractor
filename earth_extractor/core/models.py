from pydantic import BaseModel, Field, AnyUrl
import shapely.geometry
import shapely.wkt
from typing import Any, TYPE_CHECKING, Optional
from dataclasses import dataclass, asdict
import datetime
from enum import Enum


if TYPE_CHECKING:
    from earth_extractor.satellites.enums import (
        ProcessingLevel,
        Sensor,
        Satellite,
    )


class BBox(BaseModel):
    """Defines the region of interest to be used for the search

    The region of interest is defined by a list of floats. The first two
    floats define the top left corner of the rectangle, and the last two
    floats define the bottom right corner of the rectangle. The coordinates
    are in the WGS84 coordinate system.
    """

    # Limit latitude to -90 to 90
    latmin: float = Field(..., ge=-90, le=90)
    lonmin: float = Field(..., ge=-180, le=180)
    latmax: float = Field(..., ge=-90, le=90)
    lonmax: float = Field(..., ge=-180, le=180)

    @classmethod
    def from_string(cls, v: str):
        """Convert a string into a list of floats

        The string is split by a comma (',') and each element is converted
        into a float. The resulting list is returned.
        """

        if isinstance(v, str):
            values = [float(x) for x in v.split(",")]

            return cls(
                latmin=values[0],
                lonmin=values[1],
                latmax=values[2],
                lonmax=values[3],
            )

    def __str__(self):
        return f"{self.latmin},{self.lonmin},{self.latmax},{self.lonmax}"

    def to_shapely(self) -> shapely.geometry.box:
        """Convert the ROI into a shapely object

        The shapely object is a rectangle defined by the top left and bottom
        right corners of the ROI.
        """

        return shapely.geometry.box(
            self.lonmin, self.latmin, self.lonmax, self.latmax
        )


class Point(BaseModel):
    """Defines the point of interest to be used for the search"""

    # Limit latitude to -90 to 90
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)

    @classmethod
    def from_string(cls, v: str):
        """Convert a string into a list of floats

        The string is split by a comma (',') and each element is converted
        into a float. The resulting list is returned.
        """

        if isinstance(v, str):
            values = [float(x) for x in v.split(",")]

            return cls(lat=values[1], lon=values[0])

    def __str__(self):
        return f"{self.lat},{self.lon}"

    def to_shapely(self):
        """Convert the ROI into a shapely object

        The shapely object is a rectangle defined by the top left and bottom
        right corners of the ROI.
        """

        return shapely.geometry.Point(self.lon, self.lat)


@dataclass
class CommonSearchResult:
    """A class to support the exchange of search results between providers

    This class is used to standardise the search results between providers
    such that the the Provider/Satellite classes can be agnostic to the
    provider of the search results.
    """

    # Necessary for importing geojson to be able to determine provider
    satellite: "Satellite"

    product_id: Optional[Any] = None
    link: Optional[AnyUrl] = None
    identifier: Optional[str] = None
    filename: Optional[str] = None

    time: Optional[datetime.datetime] = None

    cloud_cover_percentage: Optional[float] = None
    size: Optional[float] = None

    processing_level: Optional["ProcessingLevel"] = None
    sensor: Optional["Sensor"] = None

    geometry: Optional[str] = None  # Should be as WKT
    url: Optional[AnyUrl] = None
    notes: Optional[str] = None

    # Create function to convert this dataclass to geojson including all fields
    # and casting enums to their values
    def to_geojson(self):
        """Convert this dataclass to geojson including all fields and casting
        enums to their values"""

        # Convert the dataclass to a dictionary
        d = asdict(self)

        # Convert all enums to their values
        for k, v in d.items():
            if isinstance(v, Enum):
                d[k] = v.value
        import geojson

        geom = None
        # Convert WKT geometry to shapely object
        if self.geometry is not None and isinstance(self.geometry, str):
            geom = shapely.wkt.loads(self.geometry)

        # Convert datetime to string
        if self.time is not None:
            d["time"] = self.time.isoformat()

        d.pop("geometry")  # Don't include geometry in the properties

        # Convert the dictionary to a geojson
        return geojson.Feature(geometry=geom, **d)
