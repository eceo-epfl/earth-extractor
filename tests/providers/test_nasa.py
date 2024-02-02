from earth_extractor.providers.base import Provider
from earth_extractor.providers.nasa import nasa_cmr
from earth_extractor.core.models import BBox, CommonSearchResult
from earth_extractor.satellites import enums, viirs
from datetime import datetime
import shapely.geometry
import shapely.wkt
import pytest_mock
from typing import List
from collections import OrderedDict


def test_query(
    nasa_stac_query_response: OrderedDict,
    roi_switzerland: shapely.geometry.base.BaseGeometry,
    mocker: pytest_mock.MockerFixture,
):
    """Test a query on NASA's STAC API"""

    mocker.patch.object(
        Provider,
        "query_stac",
        return_value=nasa_stac_query_response,
    )

    # Perform a nasa query
    res = nasa_cmr.query(
        satellite=viirs.viirs,
        processing_level=enums.ProcessingLevel.L1,
        roi=roi_switzerland,
        start_date=datetime(2022, 11, 19),
        end_date=datetime(2022, 11, 20),
    )

    assert isinstance(res, List)

    # Check all items are consistent and match CommonSearchResult, also check
    # individual object
    match = False
    for item in res:
        assert isinstance(item, CommonSearchResult)
        assert isinstance(item.geometry, shapely.geometry.base.BaseGeometry)
        assert item.url
        assert "LAADS:" in item.product_id
        print(item.geometry)

        if item.product_id == "LAADS:7188953671":
            match = True
            assert (
                item.url
                == "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5201/VJ103IMG/2022/323/VJ103IMG.A2022323.0042.021.2022323075217.nc"
            ), "URL does not match"
            assert item.geometry == shapely.wkt.loads(
                """
                POLYGON ((
                    55.698326 58.563728,
                    -4.459558 67.617805,
                    -1.602174 46.916576,
                    35.867203 41.203663,
                    55.698326 58.563728
                ))
                """
            ), "Geometry does not match"

    assert match is True, "Product ID 'LAADS:7188953671' not found in response"
