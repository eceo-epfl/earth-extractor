from earth_extractor.core import utils
import pyproj
import shapely
import math


def test_buffer_at_equator_in_metres():
    ''' Test buffer_in_metres function '''

    buffer_size = 10000  # 10km buffer
    # Define a point geometry on equator and perform 1000m buffer
    geom = utils.parse_roi(roi="0,0", buffer=buffer_size)

    # Reproject geometry to Web Mercator
    crs_in = pyproj.CRS.from_epsg(4326)
    crs_out = pyproj.CRS.from_epsg(3857)
    transformer = pyproj.Transformer.from_crs(crs_in, crs_out, always_xy=True)
    geom = shapely.ops.transform(transformer.transform, geom)

    # Assuming buffer on a point is a perfect circle, check radius
    radius = math.sqrt(geom.area / math.pi)
    assert math.isclose(radius, buffer_size, rel_tol=1e-3), (
        f"Radius of {radius} too far from expected: {buffer_size}"
    )


def test_buffer_at_tropics_in_metres():
    ''' Test buffer_in_metres function at tropic of cancer/capricorn '''

    buffer_size = 10000  # 10km buffer
    for latitude in ["23.5", "-23.5"]:
        # Define a point geometry on equator and perform 1000m buffer
        geom = utils.parse_roi(roi=f"{latitude},0", buffer=buffer_size)

        # Reproject geometry to Web Mercator
        crs_in = pyproj.CRS.from_epsg(4326)
        crs_out = pyproj.CRS.from_epsg(3857)
        transformer = pyproj.Transformer.from_crs(crs_in, crs_out, always_xy=True)
        geom = shapely.ops.transform(transformer.transform, geom)

        # Assuming buffer on a point is a perfect circle, check radius
        radius = math.sqrt(geom.area / math.pi)
        assert math.isclose(radius, buffer_size, rel_tol=1e-3), (
            f"Radius of {radius} too far from expected: {buffer_size}"
        )
