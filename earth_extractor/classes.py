from pydantic import BaseModel
from typing import List
from enums import ProcessingLevel, Sensor


class Satellite(BaseModel):
    name: str
    description: str | None = None
    processing_levels: List[ProcessingLevel]
    sensors: List[Sensor]


class Provider(BaseModel):
    name: str
    description: str | None = None
    satellites: List[Satellite]
    uri: str | None = None
