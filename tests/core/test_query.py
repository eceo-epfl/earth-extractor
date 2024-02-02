from earth_extractor.core import query
from earth_extractor import core, cli_options
from earth_extractor.satellites.base import Satellite
from earth_extractor.satellites import enums
from collections import OrderedDict
import os
import geopandas as gpd
import datetime
import shapely.geometry
import pytest
import pytest_mock


def test_import_query_results_to_geojson(resource_path_query) -> None:
    """Input a geojson file and check that the results are casted into the
    correct objects.
    """

    query_geojson = "sion-sentinel2-l2a.geojson"

    query_results = query.import_query_results(
        os.path.join(resource_path_query, query_geojson)
    )

    for satellite, search_result in query_results:
        assert isinstance(
            satellite, Satellite
        ), "Satellite object not defined from input query"
        for result in search_result:
            assert isinstance(
                result, core.models.CommonSearchResult
            ), "Result not casted into a CommonSearchResult object"


def test_import_query_results_to_geodataframe(resource_path_query) -> None:
    """Input geojson file such as above, but convert to a GeoDataFrame"""

    query_geojson = "sion-sentinel2-l2a.geojson"

    query_results = query.import_query_results(
        os.path.join(resource_path_query, query_geojson)
    )

    # Unpack the tuple into just search results
    all_results = []
    for satellite, search_result in query_results:
        for result in search_result:
            all_results.append(result)

    # Convert the results to a GeoDataFrame
    gdf = query.convert_query_results_to_geodataframe(all_results)

    assert isinstance(
        gdf, gpd.GeoDataFrame
    ), "GeoDataFrame not returned from query results"
    assert len(gdf) == len(all_results), (
        "Number of results in GeoDataFrame does not match number of results "
        "in query results"
    )


def test_batch_query_export_only_pipe(
    roi_switzerland: shapely.geometry.box,
    mocker: pytest_mock.MockerFixture,
    scihub_query_response: OrderedDict,
):
    """Test the batch query function with the export only pipe option

    The pipe option should exit the application

    """

    mocker.patch(
        "sentinelsat.SentinelAPI.query", return_value=scihub_query_response
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        query.batch_query(
            start=datetime.datetime(2020, 1, 1),
            end=datetime.datetime(2020, 1, 31),
            satellites=[
                cli_options.SatelliteChoices.SENTINEL2L2A,
                cli_options.SatelliteChoices.SENTINEL3L2,
            ],
            roi="45.81,5.95,47.81,10.5",
            buffer=0,
            cloud_cover=10,
            output_dir="data",
            export=cli_options.ExportMetadataOptions.PIPE,
            results_only=True,
        )

    assert pytest_wrapped_e.type == SystemExit


def test_batch_query_export_only_without_export(
    roi_switzerland: shapely.geometry.base.BaseGeometry,
):
    """Test the export only option without an export option

    Applicaiton should raise Exception

    """

    with pytest.raises(ValueError) as pytest_wrapped_e:
        query.batch_query(
            start=datetime.datetime(2020, 1, 1),
            end=datetime.datetime(2020, 1, 31),
            satellites=[
                cli_options.SatelliteChoices.SENTINEL2L2A,
                cli_options.SatelliteChoices.SENTINEL3L2,
            ],
            roi="45.81,5.95,47.81,10.5",
            buffer=0,
            cloud_cover=10,
            output_dir="data",
            export=cli_options.ExportMetadataOptions.DISABLED,
            results_only=True,
        )


def test_pair_all_cli_options() -> None:
    """Check all CLI options are pairable with a satellite and level"""

    for option in cli_options.SatelliteChoices:
        sat, level = core.utils.pair_satellite_with_level(option)
        # assert sat == 0, f"{sat} {level}"

        # Create a list of enum cli_options.Satellites values

        assert sat in [sat.value for sat in cli_options.Satellites]
        assert level in [level.value for level in enums.ProcessingLevel]
