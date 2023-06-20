import pytest
from earth_extractor.providers.copernicus import CopernicusOpenAccessHub
from earth_extractor.satellites.enums import Satellite
from earth_extractor.models import ROI


@pytest.fixture(scope="session")
def scihub():
    return CopernicusOpenAccessHub(
        name="scihub",
        description="Copernicus Open Access Hub",
        uri="https://scihub.copernicus.eu",
        satellites={
            Satellite.SENTINEL1: "Sentinel-1",
            Satellite.SENTINEL2: "Sentinel-2",
            Satellite.SENTINEL3: "Sentinel-3",
        }
    )

@pytest.fixture(scope="session")
def roi_switzerland():
    ''' Return a ROI object for the bounds of Switzerland '''

    return ROI(latmin=45.81, lonmin=5.95, latmax=47.81, lonmax=10.5)