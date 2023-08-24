from earth_extractor.providers.alaskan_satellite_facility import asf
from earth_extractor.core.models import CommonSearchResult
import pytest
import json
import pytest_mock
import asf_search
from typing import List
import requests_mock


def test_authentication_exception(
    sentinel_query_as_commonsearch_result: List[CommonSearchResult],
    mocker: pytest_mock.MockerFixture,
    caplog: pytest.LogCaptureFixture,
    tmpdir: str,
    # requests_mock: requests_mock.Mocker,
) -> None:
    """Test that an ASFAuthenticationError is raised when the credentials are
    incorrect
    """

    query = sentinel_query_as_commonsearch_result

    mocker.patch.object(
        asf_search.ASFSession,
        "auth_with_token",
        side_effect=asf_search.ASFAuthenticationError(),
    )

    asf.download_many(
        search_results=query, download_dir=str(tmpdir), overwrite=False
    )

    for important_text in [
        "ASF authentication error. ",
        "Check your credentials",
        "ASF EULA in your NASA profile at",
    ]:
        assert (
            important_text in caplog.text
        ), f"Expected text '{important_text}' not found in log message"


def test_download_many(
    mocker: pytest_mock.MockerFixture,
    sentinel_query_as_commonsearch_result: List[CommonSearchResult],
    tmpdir: str,
    caplog: pytest.LogCaptureFixture,
    requests_mock: requests_mock.Mocker,
) -> None:
    """Test the download_many functionality of asf_search

    Use the sentinel query response and mock the return responses to simulate
    a successful data collection.
    """

    requests_mock.get(
        "https://cmr.earthdata.nasa.gov/search/collections",
        content=None,
    )

    requests_mock.post(
        "https://cmr.earthdata.nasa.gov/search/granules.umm_json_v1_4",
        content=bytes(json.dumps({"items": [], "hits": 0}).encode("utf-8")),
    )
    requests_mock.post(
        "https://search-error-report.asf.alaska.edu/",
        content=None,
    )

    for sentinel_sat in ["sentinel_1", "sentinel_2", "sentinel_3"]:
        for func_name in ["download_many", "query"]:
            mocker.patch(
                "earth_extractor.satellites.sentinel."
                f"{sentinel_sat}.{func_name}",
                autospec=True,
                # return_value=None,
            )
    asf.download_many(
        search_results=sentinel_query_as_commonsearch_result,
        download_dir=str(tmpdir),
        overwrite=False,
    )

    assert (
        # Times by 2 to account for metadata files
        f"No files to download"
        in caplog.text
    ), "Expected text not found in log message"
