from typing import List
from earth_extractor.satellites import enums
from earth_extractor.providers.base import Provider


class Satellite:
    def __init__(
        self,
        query_provider: Provider,
        download_provider: Provider,
        name: enums.Satellite,
        description: str,
        processing_levels: List[enums.ProcessingLevel],
        default_level: enums.ProcessingLevel,  # Chosen if no user choice is given
        sensors: List[enums.Sensor],
    ) -> None:
        ''' A satellite's data can be queried from one provider and downloaded
            from another, defining these allows the methods to be interchanged
        '''

        self._query_provider = query_provider
        self._download_provider = download_provider

        # Use the methods from the query and download providers
        self.query = self._query_provider.query
        self.download_one = self._download_provider.download_many
        self.download_many = self._download_provider.download_many

        # General information about the satellite
        self.name = name
        self.description = description
        self.processing_levels = processing_levels
        self.default_level = default_level
        self.sensors = sensors

    def _validate_satellite_provider_compatiblity(
        self,
    ) -> None:
        ''' Check that the given provider is compatible with the satellite '''

        if self not in self._download_provider.satellites:
            raise ValueError(
                f"Satellite {self.name} not supported by download provider: "
                f"'{self._download_provider.name}'"
            )
        if self not in self._query_provider.satellites:
            raise ValueError(
                f"Satellite {self.name} not supported by query provider: "
                f"'{self._query_provider.name}'"
            )

    def __str__(self):
        ''' Return the name of the satellite as a string.

            Allows for the satellite to be used as a dictionary key
        '''

        return str(self.name)
