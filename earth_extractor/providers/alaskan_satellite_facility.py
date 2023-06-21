from earth_extractor.providers import Provider, CopernicusOpenAccessHub
from earth_extractor.satellites import enums
import logging
from typing import List, Any
import asf_search
from earth_extractor.config import credentials

logger = logging.getLogger(__name__)


class AlaskanSatteliteFacility(Provider):
    def download_from_sentinel(
        self,
        search_origin: Provider,
        search_results: List[str],
        download_dir: str = "data",
        processes: int = 6
    ) -> None:
        search_file_ids = self.process_search_results(
            search_origin, search_results
        )

        logger.info("Downloading from Alaskan Satellite Facility")
        logger.debug(f"Search file ids: {search_file_ids}")
        session = asf_search.ASFSession().auth_with_creds(
            username=credentials.NASA_USERNAME,
            password=credentials.NASA_PASSWORD
        )

        res = asf_search.granule_search(search_file_ids)
        logger.info(f"Found {len(res)} granules to download")

        if len(res) == 0:
            logger.info("No granules to download, skipping")
            return  # nothing to download

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


asf: AlaskanSatteliteFacility = AlaskanSatteliteFacility(
    name="Alaskan Satellite Facility",
    description="Alaskan Satellite Facility",
    satellites={enums.Satellite.SENTINEL1: ''},
    uri="https://asf.alaska.edu"
)
