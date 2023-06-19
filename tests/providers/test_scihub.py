from earth_extractor.satellites import sentinel_1, sentinel_2, sentinel_3
from earth_extractor.providers.scihub import CopernicusOpenAccessHub
from earth_extractor.models import ROI
from datetime import datetime


def test_query_sentinel_1():
    # Query Copernicus Open Access Hub for Sentinel-1 data

    roi = ROI(latmin=50, lonmin=100, latmax=60, lonmax=120)
    scihub = CopernicusOpenAccessHub()
    res = scihub.query(
        satellite=sentinel_1,
        roi=roi,
        start_date=datetime(2014, 11, 19),
        end_date=datetime(2014, 12, 29),
        )

    assert len(res) > 0, ("No results found")


def test_query_sentinel_2():
    # Query Copernicus Open Access Hub for Sentinel-1 data

    roi = ROI(latmin=50, lonmin=100, latmax=60, lonmax=120)
    scihub = CopernicusOpenAccessHub()
    res = scihub.query(
        satellite=sentinel_2,
        roi=roi,
        start_date=datetime(2015, 12, 19),
        end_date=datetime(2015, 12, 29),
        )

    assert len(res) > 0, ("No results found")


def test_query_sentinel_3():
    # Query Copernicus Open Access Hub for Sentinel-1 data

    roi = ROI(latmin=50, lonmin=100, latmax=60, lonmax=120)
    scihub = CopernicusOpenAccessHub()
    res = scihub.query(
        satellite=sentinel_3,
        roi=roi,
        start_date=datetime(2017, 11, 19),
        end_date=datetime(2017, 12, 29),
        )
    print(res)
    assert len(res) == 0, ("No results found")
