from typing import List
from earth_extractor.satellites import enums
from earth_extractor.providers.base import Provider
import functools
from earth_extractor import core
import logging

logger = logging.getLogger(__name__)
logger.setLevel(core.config.constants.LOGLEVEL_MODULE_DEFAULT)


class Satellite:
    def __init__(
        self,
        query_provider: Provider,
        download_provider: Provider,
        name: enums.Satellite,
        description: str,
        processing_levels: List[enums.ProcessingLevel],
        sensors: List[enums.Sensor],
        filters: List[enums.Filters],
    ) -> None:
        """A satellite's data can be queried from one provider and downloaded
        from another, defining these allows the methods to be interchanged
        """

        self._query_provider = query_provider
        self._download_provider = download_provider

        # General information about the satellite
        self.name = name
        self.description = description
        self.processing_levels = processing_levels
        self.sensors = sensors
        self.filters = filters

        # Use the methods from the query and download providers
        self.query = functools.partial(
            self._query_provider.query, satellite=self
        )
        self.download_many = functools.partial(
            self._download_provider.download_many,
        )

    @property
    def has_cloud_cover(self) -> bool:
        """Whether the satellite has a cloud cover filter"""

        return enums.Filters.CLOUD_COVER in self.filters

    def _validate_satellite_provider_compatiblity(
        self,
    ) -> None:
        """Check that the given provider is compatible with the satellite"""

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
        """Return the name of the satellite as a string.

        Allows for the satellite to be used as a dictionary key
        """

        return str(self.name)

    def __repr__(self):
        """Return the representable name of the satellite as a string."""

        return str(self.name)
