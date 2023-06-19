from earth_extractor.classes import Satellite
from earth_extractor.enums import ProcessingLevel, Sensor


sentinel_1 = Satellite(
    name="Sentinel-1",
    description="Sentinel 1",
    processing_levels=[ProcessingLevel.L1, ProcessingLevel.L2],
    sensors=[Sensor.C_SAR]
)

sentinel_2 = Satellite(
    name="Sentinel-2",
    description="Sentinel 2",
    processing_levels=[ProcessingLevel.L1C, ProcessingLevel.L2A],
    sensors=[Sensor.MSI]
)

sentinel_3 = Satellite(
    name="Sentinel-3",
    description="Sentinel 3",
    processing_levels=[ProcessingLevel.L1, ProcessingLevel.L2],
    sensors=[Sensor.OLCI, Sensor.SLSTR, Sensor.SRAL]
)