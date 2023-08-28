from typer.testing import CliRunner
from earth_extractor.app import app
from earth_extractor.core import utils
from pytest_mock import MockerFixture
from typing import List
from earth_extractor.core.models import CommonSearchResult
import asf_search
import requests
import os
import sentinelsat
import requests_mock

# from earth_extractor.providers import swiss_topo

runner = CliRunner()


def test_sentinel1_single_sat_bbox_roi(
    tmpdir: str,
    mocker: MockerFixture,
) -> None:
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
    mocker.patch.object(sentinelsat, "SentinelAPI", autospec=True)

    result = runner.invoke(
        app,
        [
            "batch",
            "--roi",
            "45.81,5.95,47.81,10.5",
            "--start",
            "2022-11-19",
            "--end",
            "2022-11-29",
            "--satellite",
            "SENTINEL1:L1",
            "--output-dir",
            tmpdir,
        ],
    )

    # As all is mocked, exit is 1 (sys.exit) as there is nothing to download
    assert result.exit_code == 1, "Expected a failed exit code"


def test_swissimage_query(
    tmpdir: str,
    mocker: MockerFixture,
    swisstopo_query_response: List[CommonSearchResult],
) -> None:
    # Mock the query function as to not actually return results
    mock_query = mocker.patch(
        # As queries are generated from the satellite, mock this call
        "earth_extractor.satellites.swissimage.swissimage.query",
        return_value=swisstopo_query_response,
    )
    mock_download_many = mocker.patch(
        "earth_extractor.satellites.swissimage.swissimage.download_many",
        # autospec=True,
        return_value=None,
    )
    mocker.patch.object(
        utils,
        "download_parallel",
        autospec=True,
        return_value=None,
    )
    res = mocker.patch.object(
        requests,
        "get",
        autospec=True,
    )
    res.raise_for_status = None

    result = runner.invoke(
        app,
        [
            "batch",
            "--roi",
            "7.35999,46.22457",
            "--buffer",
            "200",
            "--start",
            "2020-10-06",
            "--end",
            "2023-01-01",
            "--satellite",
            "swissimage:cm200",
            "--satellite",
            "swissimage:cm10",
            "--output-dir",
            str(tmpdir),
            "--no-confirmation",
        ],
    )
    print(result.stdout)
    assert mock_query.called
    assert mock_download_many.called
    assert result.exit_code == 0, "Expected to exit on success"


# def test_swissimage_query_overwrite(
#     tmpdir: str,
#     mocker: MockerFixture,
#     swisstopo_query_response: List[CommonSearchResult],
#     requests_mock: requests_mock.Mocker,
# ) -> None:
#     # Mock the query function as to not actually return results
#     mock_query = mocker.patch(
#         # As queries are generated from the satellite, mock this call
#         "earth_extractor.satellites.swissimage.swissimage.query",
#         return_value=swisstopo_query_response,
#     )

#     file_length = 50000
#     requestmocks = []
#     for query_response in swisstopo_query_response:
#         requestmocks.append(
#             requests_mock.get(
#                 str(query_response.url),
#                 content=b"a" * 500,
#                 headers={"Content-Length": f"{file_length}"},
#             )
#         )

#         # Write some fake data
#         with open(
#             os.path.join(tmpdir, query_response.url.split("/")[-1]), "w"
#         ) as f:
#             f.write("a" * file_length)

#     with open(
#         os.path.join(tmpdir, "swissimage-dop10_2020_2593-1119_2_2056.tif"), "w"
#     ) as f:
#         f.write("a" * file_length)

#     result = runner.invoke(
#         app,
#         [
#             "batch",
#             "--roi",
#             "7.35999,46.22457",
#             "--buffer",
#             "200",
#             "--start",
#             "2020-10-06",
#             "--end",
#             "2023-01-01",
#             "--satellite",
#             "swissimage:cm200",
#             "--satellite",
#             "swissimage:cm10",
#             "--output-dir",
#             str(tmpdir),
#             "--no-confirmation",
#             "--overwrite",
#         ],
#     )
#     print(result.stdout)
#     assert mock_query.called
#     assert result.exit_code == 1, "Expected to exit on success"
