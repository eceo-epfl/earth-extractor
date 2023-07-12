import pytest
from earth_extractor.core.models import BBox


@pytest.fixture(scope="session")
def roi_switzerland():
    ''' Return a ROI object for the bounds of Switzerland '''

    return BBox(
        latmin=45.81, lonmin=5.95, latmax=47.81, lonmax=10.5
    ).to_shapely()
