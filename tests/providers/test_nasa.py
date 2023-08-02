from earth_extractor.providers.base import Provider
from earth_extractor.providers.nasa import nasa_cmr
from earth_extractor.core.models import BBox, CommonSearchResult
from earth_extractor.satellites import enums, viirs
from datetime import datetime
import shapely.geometry
import pytest
import pytest_mock
import sentinelsat
import tenacity
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
    for item in res:
        assert isinstance(item, CommonSearchResult)
