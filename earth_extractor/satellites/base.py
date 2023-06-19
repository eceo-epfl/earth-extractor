from pydantic import BaseModel
from typing import List, Tuple, Generator, Callable, Any, Dict
from earth_extractor.enums import ProcessingLevel, Sensor
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from earth_extractor.config import credentials


class Satellite:
    def __init__(
        self,
        name: str,
        description: str | None = None,
        processing_levels: List[ProcessingLevel] = [],
        sensors: List[Sensor] = [],
    ) -> None:
        self.name = name
        self.description = description
        self.processing_levels = processing_levels
        self.sensors = sensors

    def __str__(self):
        return str(self.name)