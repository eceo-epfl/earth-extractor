from classes import Satellite
from enums import ProcessingLevel, Sensor


sentinel_1 = Satellite(
    name="Sentinel-1",
    description="Sentinel 1",
    processing_levels=[ProcessingLevel.L1, ProcessingLevel.L2],
    sensors=[Sensor.C_SAR]
)

sentinel_2 = Satellite(
    name="Sentinel-2",
    description="Sentinel 2",
    processing_levels=[ProcessingLevel.L1, ProcessingLevel.L2A],
    sensors=[Sensor.MSI]
)

sentinel_3 = Satellite(
    name="Sentinel-3",
    description="Sentinel 3",
    processing_levels=[ProcessingLevel.L1, ProcessingLevel.L2],
    sensors=[Sensor.OLCI, Sensor.SLSTR, Sensor.SRAL]
)

satellites = [sentinel_1, sentinel_2, sentinel_3]
