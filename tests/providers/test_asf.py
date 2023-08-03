from earth_extractor.providers.alaskan_satellite_facility import asf
from earth_extractor.core.models import CommonSearchResult
import pytest
import pytest_mock
import asf_search


def test_authentication_exception(
    sentinel_query_as_commonsearch_result: list[CommonSearchResult],
    mocker: pytest_mock.MockerFixture,
    caplog: pytest.LogCaptureFixture
) -> None:
    ''' Test that an ASFAuthenticationError is raised when the credentials are
        incorrect
    '''

    query = sentinel_query_as_commonsearch_result

    mocker.patch.object(
        asf_search.ASFSession, 'auth_with_creds',
        side_effect=asf_search.ASFAuthenticationError()
    )

    # with pytest.raises(asf_search.ASFAuthenticationError):
    asf.download_many(
        search_results=query,
        download_dir='asf_testdata',
    )

    for important_text in [
        "ASF authentication error. ",
        "Check your credentials",
        "ASF EULA in your NASA profile at"
    ]:
        assert important_text in caplog.text, (
            f"Expected text '{important_text}' not found in log message"
        )
