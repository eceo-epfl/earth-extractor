"""Extended asf_search download with overwrite support and progress bars.

The upstream asf_search library does not support overwriting existing files.
This module wraps the download process to add that capability.
"""

import os
import urllib.parse
import warnings
import tqdm
from earth_extractor import core
from asf_search.download.download import _try_get_response
from asf_search.exceptions import ASFDownloadError
import logging
from asf_search.ASFSearchResults import ASFSearchResults
from asf_search.ASFSession import ASFSession
from asf_search.ASFProduct import ASFProduct
from asf_search.download.file_download_type import FileDownloadType
from concurrent.futures import ThreadPoolExecutor, as_completed
import asf_search

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


def download_url(
    url: str,
    path: str,
    filename: str = None,
    session: ASFSession = None,
    overwrite: bool = False,
) -> None:
    """Downloads a product from the specified URL with overwrite support."""
    if filename is None:
        filename = os.path.split(urllib.parse.urlparse(url).path)[1]

    if not os.path.isdir(path):
        raise ASFDownloadError(
            f"Error downloading {url}: directory not found: {path}"
        )

    if os.path.isfile(os.path.join(path, filename)):
        logger.info(
            f"File already exists: {filename} "
            f"... {'Overwriting' if overwrite else 'Skipping'}"
        )
        if not overwrite:
            return

    if session is None:
        session = ASFSession()

    response = _try_get_response(session=session, url=url)
    total_size = int(response.headers.get("content-length", -1))

    with open(os.path.join(path, filename), "wb") as dest:
        with tqdm.tqdm(
            total=total_size,
            desc=url,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    size = dest.write(chunk)
                    bar.update(size)


def download_results(
    results: ASFSearchResults,
    path: str,
    session: ASFSession = None,
    processes: int = 1,
    fileType=FileDownloadType.DEFAULT_FILE,
    overwrite: bool = False,
) -> None:
    """Download ASF search results with overwrite support."""
    logger.info(f"Started downloading {len(results)} results.")

    if processes == 1:
        for product in results:
            _download_product_with_overwrite(
                product, path, session, fileType, overwrite
            )
    else:
        logger.info(f"Using {processes} threads.")
        with ThreadPoolExecutor(max_workers=processes) as executor:
            futures = {
                executor.submit(
                    _download_product_with_overwrite,
                    product, path, session, fileType, overwrite,
                )
                for product in results
            }
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"ASF download error: {e}")


def _download_product_with_overwrite(
    product: ASFProduct,
    path: str,
    session: ASFSession = None,
    fileType=FileDownloadType.DEFAULT_FILE,
    overwrite: bool = False,
) -> None:
    """Download a single ASF product with overwrite support."""
    if session is None:
        session = product.session

    filename = product.properties.get("fileName", "")

    urls = []
    if fileType in (FileDownloadType.DEFAULT_FILE, FileDownloadType.ALL_FILES):
        urls.append((filename, product.properties["url"]))
    if fileType in (
        FileDownloadType.ADDITIONAL_FILES,
        FileDownloadType.ALL_FILES,
    ):
        base = ".".join(filename.split(".")[:-1])
        for url in product.properties.get("additionalUrls", []):
            ext = url.split(".")[-1]
            urls.append((f"{base}.{ext}", url))

    for fname, url in urls:
        download_url(
            url=url,
            path=path,
            filename=fname,
            session=session,
            overwrite=overwrite,
        )


def granule_search(granule_list, **kwargs) -> ASFSearchResults:
    """Search for granules using the standard asf_search API."""
    return asf_search.granule_search(granule_list=granule_list, **kwargs)
