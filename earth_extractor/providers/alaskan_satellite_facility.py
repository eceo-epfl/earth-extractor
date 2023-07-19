from earth_extractor.providers import Provider
from earth_extractor.satellites import enums
import logging
from typing import List
import asf_search
from earth_extractor.core.credentials import get_credentials
from earth_extractor import core


logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

credentials = get_credentials()


class AlaskanSateliteFacility(Provider):
    def download_many(
        self,
        search_results: List[core.models.CommonSearchResult],
        download_dir: str,
        processes: int = 6
    ) -> None:

        # Extract the file ids from the search results
        search_file_ids = [result.identifier for result in search_results]

        logger.info("Downloading from Alaskan Satellite Facility")
        logger.debug(f"Search file ids: {search_file_ids}")

        # Add the ASF logger to the root logger
        asf_logger = logging.getLogger("asf_search")
        asf_logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

        self.create_download_folder(download_dir)  # Create the download folder

        # Authenticate with ASF
        try:
            session = asf_search.ASFSession().auth_with_creds(
                username=credentials.NASA_USERNAME,
                password=credentials.NASA_PASSWORD
            )

            # Search for the granules
            res = asf_search.granule_search(search_file_ids)
            logger.info(
                f"Found {len(res)} files to download (may include "
                "metadata files)"
            )

            if len(res) == 0:
                logger.info("No files to download, skipping")
                return  # nothing to download

            # Download the granules using the ASF API library
            res.download(
                path=download_dir,
                session=session,
                processes=processes
            )
        except asf_search.ASFAuthenticationError as e:
            logger.error(
                "ASF authentication error. Check your credentials and make "
                "sure that you have accepted the ASF EULA in your NASA "
                "profile at "
                "https://urs.earthdata.nasa.gov/users/ejayt/unaccepted_eulas"
            )
            logger.debug(f"ASF Authentication error: {e}")
            return


asf: AlaskanSateliteFacility = AlaskanSateliteFacility(
    name="Alaskan Satellite Facility",
    description="Alaskan Satellite Facility",
    satellites={enums.Satellite.SENTINEL1: ''},
    uri="https://asf.alaska.edu"
)
