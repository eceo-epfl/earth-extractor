from earth_extractor.core import query
from earth_extractor.core.models import CommonSearchResult
from earth_extractor.satellites.base import Satellite
import os
import geopandas as gpd


def test_import_query_results_to_geojson(
    resource_path_query
) -> None:
    ''' Input a geojson file and check that the results are casted into the
        correct objects.
    '''

    query_geojson = 'sion-sentinel2-l2a.geojson'

    query_results = query.import_query_results(
        os.path.join(
            resource_path_query,
            query_geojson
        )
    )

    for satellite, search_result in query_results:
        assert isinstance(satellite, Satellite), (
            "Satellite object not defined from input query"
        )
        for result in search_result:
            assert isinstance(result, CommonSearchResult), (
                "Result not casted into a CommonSearchResult object"
            )


def test_import_query_results_to_geodataframe(
        resource_path_query
) -> None:
    ''' Input geojson file such as above, but convert to a GeoDataFrame '''

    query_geojson = 'sion-sentinel2-l2a.geojson'

    query_results = query.import_query_results(
        os.path.join(
            resource_path_query,
            query_geojson
        )
    )

    # Unpack the tuple into just search results
    all_results = []
    for satellite, search_result in query_results:
        for result in search_result:
            all_results.append(result)

    # Convert the results to a GeoDataFrame
    gdf = query.convert_query_results_to_geodataframe(
        all_results
    )

    assert isinstance(gdf, gpd.GeoDataFrame), (
        "GeoDataFrame not returned from query results"
    )
    assert len(gdf) == len(all_results), (
        "Number of results in GeoDataFrame does not match number of results "
        "in query results"
    )
