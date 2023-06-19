from classes import Provider
from satellites import sentinel_1, sentinel_2, sentinel_3
from scihub import query


asf = Provider(
    name="Alaskan Satellite Facility",
    description="Alaskan Satellite Facility",
    satellites=[(sentinel_1, '')],
    uri="https://asf.alaska.edu"
)

scihub = Provider(
    name="SciHub",
    description="SciHub",
    satellites=[
        (sentinel_1, 'Sentinel-1'),
        (sentinel_2, 'Sentinel-2'),
        (sentinel_3, 'Sentinel-3'),
    ],
    uri="https://scihub.copernicus.eu",
    query=query()
)

cmr = Provider(
    name="CMR",
    description="Common Metadata Repository",
    satellites=[(sentinel_3, '')],
    uri="https://cmr.earthdata.nasa.gov"
)

sinergise = Provider(
    name="Sinergise",
    description="Sinergise",
    satellites=[(sentinel_2, '')],
    uri="https://www.sinergise.com"
)
