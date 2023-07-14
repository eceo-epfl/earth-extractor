from earth_extractor.providers.copernicus import copernicus_scihub
from earth_extractor.core.models import BBox
from datetime import datetime
import pytest
import sentinelsat
import tenacity


def test_wait_on_download_exception(
    scihub_query_response,
    mocker
):
    ''' Test that Tenacity will wait and retry on the download_many() function

        API will fail on > 90 requests per minute, so test retrying on failure
        but with no wait time and only 1 retry attempt
    '''

    #
    mocker.patch(
        'sentinelsat.SentinelAPI.download_all',
        side_effect=sentinelsat.exceptions.ServerError("Test exception")
        # return_value=expected_response
    )
    results_common_format = copernicus_scihub.translate_search_results(
        scihub_query_response
    )

    # Overwrite tenacity's retry function to only retry once and not wait
    copernicus_scihub.download_many.retry.wait = tenacity.wait_none()

    # Make sure
    with pytest.raises(sentinelsat.exceptions.ServerError):
        res = copernicus_scihub.download_many(
            search_results=results_common_format,
            download_dir='testdata',
        )
