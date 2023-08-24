""" Functions from the sentinelsat library, modified to allow overwriting of
existing files.

Full repository: https://github.com/sentinelsat/sentinelsat
"""


from sentinelsat import SentinelAPI, Downloader, DownloadStatus
from sentinelsat.download import _format_exception
from collections import namedtuple
import threading
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import itertools
from sentinelsat.exceptions import (
    SentinelAPIError,
)
from copy import copy


class SentinelAPIExtended(SentinelAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.downloader = DownloaderExtended(self)  # @evanjt: Add ext. class

    def download_all(
        self,
        products,
        directory_path=".",
        max_attempts=10,
        checksum=True,
        n_concurrent_dl=None,
        lta_retry_delay=None,
        fail_fast=False,
        nodefilter=None,
        overwrite=False,
    ):
        """Download a list of products.

        Takes a list of product IDs as input. This means that the return value of query() can be
        passed directly to this method.

        File names on the server are used for the downloaded files, e.g.
        "S1A_EW_GRDH_1SDH_20141003T003840_20141003T003920_002658_002F54_4DD1.zip".

        In case of interruptions or other exceptions, downloading will restart from where it left
        off. Downloading is attempted at most max_attempts times to avoid getting stuck with
        unrecoverable errors.

        Parameters
        ----------
        products : list
            List of product IDs
        directory_path : string
            Directory where the downloaded files will be downloaded
        max_attempts : int, default 10
            Number of allowed retries before giving up downloading a product.
        checksum : bool, default True
            If True, verify the downloaded files' integrity by checking its MD5 checksum.
            Throws InvalidChecksumError if the checksum does not match.
            Defaults to True.
        n_concurrent_dl : integer, optional
            Number of concurrent downloads. Defaults to :attr:`SentinelAPI.concurrent_dl_limit`.
        lta_retry_delay : float, default 60
            Number of seconds to wait between requests to the Long Term Archive.
        fail_fast : bool, default False
            if True, all other downloads are cancelled when one of the downloads fails.
        nodefilter : callable, optional
            The callable is used to select which files of each product will be downloaded.
            If None (the default), the full products will be downloaded.
            See :mod:`sentinelsat.products` for sample node filters.
        overwrite: bool, default False
            If True, existing files will be overwritten. If False, existing files will be skipped.
        Notes
        -----
        By default, raises the most recent downloading exception if all downloads failed.
        If ``fail_fast`` is set to True, raises the encountered exception on the first failed
        download instead.

        Returns
        -------
        dict[string, dict]
            A dictionary containing the return value from download() for each successfully
            downloaded product.
        dict[string, dict]
            A dictionary containing the product information for products successfully
            triggered for retrieval from the long term archive but not downloaded.
        dict[string, dict]
            A dictionary containing the product information of products where either
            downloading or triggering failed. "exception" field with the exception info
            is included to the product info dict.
        """
        downloader = copy(self.downloader)
        downloader.verify_checksum = checksum
        downloader.fail_fast = fail_fast
        downloader.max_attempts = max_attempts
        if n_concurrent_dl:
            downloader.n_concurrent_dl = n_concurrent_dl
        if lta_retry_delay:
            downloader.lta_retry_delay = lta_retry_delay
        downloader.node_filter = nodefilter
        statuses, exceptions, product_infos = downloader.download_all(
            products, directory_path, overwrite=overwrite
        )

        # Adapt results to the old download_all() API
        downloaded_prods = {}
        retrieval_triggered = {}
        failed_prods = {}
        for pid, status in statuses.items():
            if pid not in product_infos:
                product_infos[pid] = {}
            if pid in exceptions:
                product_infos[pid]["exception"] = exceptions[pid]
            if status == DownloadStatus.DOWNLOADED:
                downloaded_prods[pid] = product_infos[pid]
            elif status == DownloadStatus.TRIGGERED:
                retrieval_triggered[pid] = product_infos[pid]
            else:
                failed_prods[pid] = product_infos[pid]
        ResultTuple = namedtuple(
            "ResultTuple", ["downloaded", "retrieval_triggered", "failed"]
        )
        return ResultTuple(downloaded_prods, retrieval_triggered, failed_prods)


class DownloaderExtended(Downloader):
    def download_all(self, products, directory=".", overwrite=False):
        """Download a list of products.

        Parameters
        ----------
        products : list
            List of product IDs
        directory : string or Path, optional
            Directory where the files will be downloaded

        Notes
        ------
        By default, raises the most recent downloading exception if all downloads failed.
        If :attr:`Downloader.fail_fast` is set to True, raises the encountered exception on the first failed
        download instead.

        Returns
        -------
        dict[string, DownloadStatus]
            The status of all products.
        dict[string, Exception]
            Exception info for any failed products.
        dict[string, dict]
            A dictionary containing the product information for each product
            (unless the product was unavailable).
        """

        ResultTuple = namedtuple(
            "ResultTuple", ["statuses", "exceptions", "product_infos"]
        )
        product_ids = list(set(products))
        assert self.n_concurrent_dl > 0
        if len(product_ids) == 0:
            return ResultTuple({}, {}, {})
        self.logger.info(
            "Will download %d products using %d workers",
            len(product_ids),
            self.n_concurrent_dl,
        )

        (
            statuses,
            online_prods,
            offline_prods,
            product_infos,
            exceptions,
        ) = self._init_statuses(product_ids)

        # Skip already downloaded files.
        # Although the download method also checks, we do not need to retrieve such
        # products from the LTA and use up our quota.
        if not overwrite:  # @evanjt skip this check if overwrite is True
            self._skip_existing_products(
                directory, offline_prods, product_infos, statuses, exceptions
            )

        stop_event = threading.Event()
        dl_tasks = {}
        trigger_tasks = {}

        # Two separate threadpools for downloading and triggering of retrieval.
        # Otherwise triggering might take up all threads and nothing is downloaded.
        dl_count = len(online_prods) + len(offline_prods)
        dl_executor = ThreadPoolExecutor(
            max_workers=max(1, min(self.n_concurrent_dl, dl_count)),
            thread_name_prefix="dl",
        )
        dl_progress = self._tqdm(
            total=dl_count,
            desc="Downloading products",
            unit="product",
        )
        if offline_prods:
            trigger_executor = ThreadPoolExecutor(
                max_workers=min(
                    self.api.concurrent_lta_trigger_limit, len(offline_prods)
                ),
                thread_name_prefix="trigger",
            )
            trigger_progress = self._tqdm(
                total=len(offline_prods),
                desc="LTA retrieval",
                unit="product",
                leave=True,
            )
        try:
            # First all online products are downloaded. Subsequently, offline products that might
            # have become available in the meantime are requested.
            for pid in itertools.chain(online_prods, offline_prods):
                future = dl_executor.submit(
                    self._download_online_retry,
                    product_infos[pid],
                    directory,
                    statuses,
                    exceptions,
                    stop_event,
                )
                dl_tasks[future] = pid

            for pid in offline_prods:
                future = trigger_executor.submit(
                    self._trigger_and_wait,
                    pid,
                    stop_event,
                    statuses,
                )
                trigger_tasks[future] = pid

            for task in concurrent.futures.as_completed(
                list(trigger_tasks) + list(dl_tasks)
            ):
                pid = trigger_tasks.get(task) or dl_tasks[task]
                exception = exceptions.get(pid)
                if task.cancelled():
                    exception = concurrent.futures.CancelledError()
                if task.exception():
                    exception = task.exception()

                if task in dl_tasks:
                    if not exception:
                        product_infos[pid] = task.result()
                        statuses[pid] = DownloadStatus.DOWNLOADED
                    dl_progress.update()
                    # Keep the LTA progress fresh
                    if offline_prods:
                        trigger_progress.update(0)
                else:
                    trigger_progress.update()
                    if all(t.done() for t in trigger_tasks):
                        trigger_progress.close()

                if exception:
                    exceptions[pid] = exception
                    if self.fail_fast:
                        raise exception from None
                    else:
                        self.logger.error(
                            "%s failed: %s", pid, _format_exception(exception)
                        )
        except:
            stop_event.set()
            for t in list(trigger_tasks) + list(dl_tasks):
                t.cancel()
            raise
        finally:
            dl_executor.shutdown()
            dl_progress.close()
            if offline_prods:
                trigger_executor.shutdown()
                trigger_progress.close()

        if not any(statuses):
            if not exceptions:
                raise SentinelAPIError(
                    "Downloading all products failed for an unknown reason"
                )
            exception = list(exceptions)[0]
            raise exception

        # Update Online status in product_infos
        for pid, status in statuses.items():
            if status in [DownloadStatus.OFFLINE, DownloadStatus.TRIGGERED]:
                product_infos[pid]["Online"] = False
            elif status != DownloadStatus.UNAVAILABLE:
                product_infos[pid]["Online"] = True

        return ResultTuple(statuses, exceptions, product_infos)
