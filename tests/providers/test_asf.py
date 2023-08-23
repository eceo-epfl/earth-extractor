from earth_extractor.providers.alaskan_satellite_facility import asf
from earth_extractor.core.models import CommonSearchResult
import pytest
import pytest_mock
import asf_search
import os
from typing import List


def test_authentication_exception(
    sentinel_query_as_commonsearch_result: List[CommonSearchResult],
    mocker: pytest_mock.MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that an ASFAuthenticationError is raised when the credentials are
    incorrect
    """

    query = sentinel_query_as_commonsearch_result

    mocker.patch.object(
        asf_search.ASFSession,
        "auth_with_creds",
        side_effect=asf_search.ASFAuthenticationError(),
    )

    # with pytest.raises(asf_search.ASFAuthenticationError):
    asf.download_many(
        search_results=query,
        download_dir="asf_testdata",
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
) -> None:
    """Test the download_many functionality of asf_search

    Use the sentinel query response and mock the return responses to simulate
    a successful data collection.
    """
    mocker.patch.object(
        asf_search.ASFSession,
        "auth_with_token",
        return_value=None,
    )
    mocker.patch.object(
        asf_search.ASFProduct,
        "download",
        return_value=None,
        autospec=True,
    )
    mocker.patch.object(
        asf_search.ASFSearchResults,
        "download",
        return_value=None,
        autospec=True,
    )

    res = asf.download_many(
        sentinel_query_as_commonsearch_result,
        download_dir=tmpdir,
        overwrite=False,
    )

    assert (
        # Times by 2 to account for metadata files
        f"Found {len(sentinel_query_as_commonsearch_result)*2} files to "
        "download" in caplog.text
    ), "Expected text not found in log message"
    os.path.exists(tmpdir)
