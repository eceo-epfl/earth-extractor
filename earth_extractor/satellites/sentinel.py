from earth_extractor.satellites.base import Satellite
from earth_extractor.satellites import enums
from earth_extractor.providers import copernicus_scihub, asf


''' Define the Sentinel satellites '''

sentinel_1: Satellite = Satellite(
    query_provider=copernicus_scihub,
    download_provider=asf,
    name=enums.Satellite.SENTINEL1,
    description="Sentinel 1",
    processing_levels=[enums.ProcessingLevel.L1, enums.ProcessingLevel.L2],
    sensors=[enums.Sensor.C_SAR]
)

sentinel_2: Satellite = Satellite(
    query_provider=copernicus_scihub,
    download_provider=copernicus_scihub,
    name=enums.Satellite.SENTINEL2,
    description="Sentinel 2",
    processing_levels=[enums.ProcessingLevel.L1C, enums.ProcessingLevel.L2A],
    sensors=[enums.Sensor.MSI]
)

sentinel_3: Satellite = Satellite(
    query_provider=copernicus_scihub,
    download_provider=copernicus_scihub,
    name=enums.Satellite.SENTINEL3,
    description="Sentinel 3",
    processing_levels=[enums.ProcessingLevel.L1, enums.ProcessingLevel.L2],
    sensors=[enums.Sensor.OLCI, enums.Sensor.SLSTR, enums.Sensor.SRAL]
)
