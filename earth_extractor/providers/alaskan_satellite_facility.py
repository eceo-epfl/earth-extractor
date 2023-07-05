from earth_extractor.providers import Provider, CopernicusOpenAccessHub
from earth_extractor.satellites import enums
import logging
from typing import List, Any
import asf_search
from earth_extractor.core.credentials import get_credentials
from earth_extractor import core


logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_CONSOLE)

credentials = get_credentials()


class AlaskanSateliteFacility(Provider):
    def download_many(
        self,
        search_origin: Provider,
        search_results: List[str],
        download_dir: str,
        processes: int = 6
    ) -> None:

        # Extract the file ids from the search results
        search_file_ids = self.process_search_results(
            search_origin, search_results
        )

        logger.info("Downloading from Alaskan Satellite Facility")
        logger.debug(f"Search file ids: {search_file_ids}")

        # Add the ASF logger to the root logger
        logger.addHandler(asf_search.ASF_LOGGER)
        self.create_download_folder(download_dir)  # Create the download folder

        # Authenticate with ASF
        try:
            session = asf_search.ASFSession().auth_with_creds(
                username=credentials.NASA_USERNAME,
                password=credentials.NASA_PASSWORD
            )
        except asf_search.ASFAuthenticationError as e:
            logger.error(f"ASF authentication error: {e}")
            return

        # Search for the granules
        res = asf_search.granule_search(search_file_ids)
        logger.info(f"Found {len(res)} granules to download")

        if len(res) == 0:
            logger.info("No granules to download, skipping")
            return  # nothing to download

        # Download the granules using the ASF API library
        res.download(path=download_dir, session=session, processes=processes)

    def process_search_results(
        self,
        origin: Provider,
        results: Any
    ) -> List[str]:
        ''' Process search results to a compatible format for ASF

        Define a mapping of search results from a given provider to another
        provider. This is necessary because the search results from Copernicus
        Open Access Hub, for example, are not compatible with ASF.

        Parameters
        ----------
        origin : Provider
            The provider of the search results
        results : Any
            The search results

        Returns
        -------
        List[str]
            The search results in a compatible format for ASF
        '''
        if isinstance(origin, CopernicusOpenAccessHub):
            return [prop['identifier'] for id, prop in results.items()]

        if isinstance(origin, self.__class__):
            return results

        return []


asf: AlaskanSateliteFacility = AlaskanSateliteFacility(
    name="Alaskan Satellite Facility",
    description="Alaskan Satellite Facility",
    satellites={enums.Satellite.SENTINEL1: ''},
    uri="https://asf.alaska.edu"
)
