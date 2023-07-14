import pytest
from earth_extractor.core.models import BBox
import os


@pytest.fixture(scope="session")
def roi_switzerland():
    ''' Return a ROI object for the bounds of Switzerland '''

    return BBox(
        latmin=45.81, lonmin=5.95, latmax=47.81, lonmax=10.5
    ).to_shapely()


@pytest.fixture(scope="session")
def resource_path_roi():
    ''' Return the path to the test ROI resources '''

    return os.path.join(
        os.getcwd(),
        "tests",
        "resources",
        "roi"
    )

@pytest.fixture(scope="session")
def resource_path_query():
    ''' Return the path to the test query resources '''

    return os.path.join(
        os.getcwd(),
        "tests",
        "resources",
        "query"
    )
