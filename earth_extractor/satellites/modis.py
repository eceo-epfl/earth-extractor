from earth_extractor.satellites.base import Satellite
from earth_extractor.satellites import enums

# from earth_extractor.providers import copernicus_scihub, asf
from earth_extractor.providers import nasa_cmr


""" Define the MODIS constellation """

modis_terra: Satellite = Satellite(
    query_provider=nasa_cmr,
    download_provider=nasa_cmr,
    name=enums.Satellite.MODIS_TERRA,
    description="Sentinel 1",
    processing_levels=[enums.ProcessingLevel.L1B],
    sensors=[enums.Sensor.MODIS],
    filters=[enums.Filters.CLOUD_COVER],
)

modis_aqua: Satellite = Satellite(
    query_provider=nasa_cmr,
    download_provider=nasa_cmr,
    name=enums.Satellite.MODIS_AQUA,
    description="Sentinel 1",
    processing_levels=[enums.ProcessingLevel.L1B],
    sensors=[enums.Sensor.MODIS],
    filters=[enums.Filters.CLOUD_COVER],
)
