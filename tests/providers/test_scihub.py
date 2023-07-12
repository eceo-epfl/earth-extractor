from earth_extractor.satellites.sentinel import (
    sentinel_1, sentinel_2, sentinel_3
)
from earth_extractor.providers.copernicus import copernicus_scihub
from earth_extractor.core.models import BBox
from earth_extractor.satellites.enums import Satellite
from earth_extractor.satellites.enums import ProcessingLevel
from datetime import datetime


''' These following tests require access to the API -- probably not the best
    way to do this, but it helps in early development.
'''

def test_query_sentinel_1(
    roi_switzerland: BBox
):
    # Query Copernicus Open Access Hub for Sentinel-1 data
    res = copernicus_scihub.query(
        satellite=sentinel_1,
        roi=roi_switzerland,
        start_date=datetime(2016, 11, 19),
        end_date=datetime(2016, 12, 29),
        processing_level=ProcessingLevel.L1
        )

    assert len(res) > 0, ("No results found")


def test_query_sentinel_2(
    roi_switzerland: BBox
):
    # Query Copernicus Open Access Hub for Sentinel-1 data
    res = copernicus_scihub.query(
        satellite=sentinel_2,
        roi=roi_switzerland,
        start_date=datetime(2015, 12, 19),
        end_date=datetime(2015, 12, 29),
        processing_level=ProcessingLevel.L1C
        )

    assert len(res) > 0, ("No results found")


def test_query_sentinel_3(
    roi_switzerland: BBox
):
    # Query Copernicus Open Access Hub for Sentinel-3 data
    res = copernicus_scihub.query(
        satellite=sentinel_3,
        roi=roi_switzerland,
        start_date=datetime(2017, 11, 19),
        end_date=datetime(2017, 12, 29),
        processing_level=ProcessingLevel.L2
        )

    assert len(res) == 37, ("Found results when shouldn't have")  # Too rigid?

def test_wait_on_download_exception():
    ''' Test that Tenacity will wait and retry on the download_many() function

        API will fail on > 90 requests per minute, so test retrying on failure
    '''

    # Query Copernicus Open Access Hub for Sentinel-1 data
    res = copernicus_scihub.query(
        satellite=sentinel_1,
        roi=BBox.from_string("0,0,1,1"),
        start_date=datetime(2016, 11, 19),
        end_date=datetime(2016, 12, 29),
        processing_level=ProcessingLevel.L1
    )
