from earth_extractor.satellites.sentinel import (
    sentinel_1, sentinel_2, sentinel_3
)
from earth_extractor.providers.copernicus import CopernicusOpenAccessHub
from earth_extractor.models import ROI
from earth_extractor.satellites.enums import Satellite
from datetime import datetime


def test_query_sentinel_1(
    scihub: CopernicusOpenAccessHub,
    roi_switzerland: ROI
):
    # Query Copernicus Open Access Hub for Sentinel-1 data
    res = scihub.query(
        satellite=sentinel_1,
        roi=roi_switzerland,
        start_date=datetime(2016, 11, 19),
        end_date=datetime(2016, 12, 29),
        )

    assert len(res) > 0, ("No results found")


def test_query_sentinel_2(
    scihub: CopernicusOpenAccessHub,
    roi_switzerland: ROI
):
    # Query Copernicus Open Access Hub for Sentinel-1 data
    res = scihub.query(
        satellite=sentinel_2,
        roi=roi_switzerland,
        start_date=datetime(2015, 12, 19),
        end_date=datetime(2015, 12, 29),
        )

    assert len(res) > 0, ("No results found")


def test_query_sentinel_3(
    scihub: CopernicusOpenAccessHub,
    roi_switzerland: ROI
):
    # Query Copernicus Open Access Hub for Sentinel-3 data
    res = scihub.query(
        satellite=sentinel_3,
        roi=roi_switzerland,
        start_date=datetime(2017, 11, 19),
        end_date=datetime(2017, 12, 29),
        )

    assert len(res) == 0, ("No results found")
