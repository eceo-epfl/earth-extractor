from earth_extractor.providers import Provider
import logging
from typing import List
import asf_search
from earth_extractor.core.credentials import get_credentials
from earth_extractor import core
from earth_extractor.providers.extensions.asf_search import granule_search

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

credentials = get_credentials()


class AlaskanSateliteFacility(Provider):
    def download_many(
        self,
        search_results: List[core.models.CommonSearchResult],
        download_dir: str,
        overwrite: bool = False,
        processes: int = 6,
    ) -> None:
        """Download many files from the Alaskan Satellite Facility"""

        # Check that the provider's credentials that are needed are set
        self._check_credentials_exist()

        # Extract the file ids from the search results
        search_file_ids = [
            result.identifier
            for result in search_results
            if result.identifier is not None
        ]

        logger.info("Downloading from Alaskan Satellite Facility")
        logger.debug(f"Search file ids: {search_file_ids}")

        # Add the ASF logger to the root logger
        asf_logger = logging.getLogger("asf_search")
        asf_logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)

        self.create_download_folder(download_dir)  # Create the download folder

        # Authenticate with ASF
        try:
            session = asf_search.ASFSession().auth_with_token(
                token=credentials.NASA_TOKEN,
            )

            # Search for the granules
            res = granule_search(search_file_ids)
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
                processes=processes,
                overwrite=overwrite,
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
    uri="https://asf.alaska.edu",
    credentials_required=["NASA_TOKEN"],
)
