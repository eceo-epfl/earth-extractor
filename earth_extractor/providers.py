from classes import Provider
from satellites import SENTINEL1, SENTINEL2, SENTINEL3


asf = Provider(
    name="Alaskan Satellite Facility",
    description="Alaskan Satellite Facility",
    satellites=[SENTINEL1],
    uri="https://asf.alaska.edu"
)

scihub = Provider(
    name="SciHub",
    description="SciHub",
    satellites=[SENTINEL2],
    uri="https://scihub.copernicus.eu"
)

cmr = Provider(
    name="CMR",
    description="Common Metadata Repository",
    satellites=[SENTINEL3],
    uri="https://cmr.earthdata.nasa.gov"
)

sinergise = Provider(
    name="Sinergise",
    description="Sinergise",
    satellites=[SENTINEL2],
    uri="https://www.sinergise.com"
)
