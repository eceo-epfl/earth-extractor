from earth_extractor.providers.copernicus import copernicus_scihub
import pytest
import pytest_mock
import sentinelsat
import tenacity
from collections import OrderedDict


def test_wait_on_download_exception(
    scihub_query_response: OrderedDict,
    mocker: pytest_mock.MockerFixture
):
    ''' Test that Tenacity will wait and retry on the download_many() function

        API will fail on > 90 requests per minute, so test retrying on failure
        but with no wait time and only 1 retry attempt
    '''

    mocker.patch(
        'sentinelsat.SentinelAPI.download_all',
        side_effect=sentinelsat.exceptions.ServerError("Test exception")
    )
    results_common_format = copernicus_scihub.translate_search_results(
        scihub_query_response
    )

    # Overwrite tenacity's retry function to only retry once and not wait
    copernicus_scihub.download_many.retry.wait = tenacity.wait_none()

    # Make sure the exception is raised
    with pytest.raises(sentinelsat.exceptions.ServerError):
        copernicus_scihub.download_many(
            search_results=results_common_format,
            download_dir='testdata',
        )
