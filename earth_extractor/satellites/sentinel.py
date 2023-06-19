from earth_extractor.satellites.base import Satellite
from earth_extractor.enums import ProcessingLevel, Sensor
from earth_extractor import providers


sentinel_1 = Satellite(
    query_provider=providers.copernicus_scihub,
    download_provider=providers.asf,
    name="Sentinel-1",
    description="Sentinel 1",
    processing_levels=[ProcessingLevel.L1, ProcessingLevel.L2],
    sensors=[Sensor.C_SAR]
)

sentinel_2 = Satellite(
    query_provider=providers.copernicus_scihub,
    download_provider=providers.sinergise,
    name="Sentinel-2",
    description="Sentinel 2",
    processing_levels=[ProcessingLevel.L1C, ProcessingLevel.L2A],
    sensors=[Sensor.MSI]
)

sentinel_3 = Satellite(
    query_provider=providers.nasa_cmr,
    download_provider=providers.nasa_cmr,
    name="Sentinel-3",
    description="Sentinel 3",
    processing_levels=[ProcessingLevel.L1, ProcessingLevel.L2],
    sensors=[Sensor.OLCI, Sensor.SLSTR, Sensor.SRAL]
)
