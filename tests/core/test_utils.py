from earth_extractor.core import utils
import pyproj
import shapely.ops


def test_buffer_in_metres():
    ''' Test buffer_in_metres function '''

    # Define a geometry and perform buffer
    geom = utils.parse_roi("0,0,1,1")
    buffered_geom = utils.buffer_in_metres(geom, 5000)

    # Reproject geometry to Web Mercator
    crs_in = pyproj.CRS.from_epsg(4326)
    crs_out = pyproj.CRS.from_epsg(3857)
    transformer = pyproj.Transformer.from_crs(crs_in, crs_out, always_xy=True)

    projected_geom = shapely.ops.transform(transformer.transform, geom)
    projected_buffered_geom = shapely.ops.transform(transformer.transform,
                                                    buffered_geom)

    with open('test.geojson', 'w') as f:
        f.write(shapely.to_geojson(geom))
    # assert shapely.to_geojson(projected_geom) == 0
    difference = projected_buffered_geom.length - projected_geom.length

    assert difference == 0
