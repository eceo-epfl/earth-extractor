# flake8: noqa
import pytest
from earth_extractor.core.models import BBox, CommonSearchResult
from earth_extractor.core.credentials import Credentials
from earth_extractor.satellites.enums import Satellite, ProcessingLevel
from earth_extractor.providers import copernicus_dataspace
import os
import orjson
import shapely.geometry
from collections import OrderedDict
import datetime
from typing import List


@pytest.fixture(scope="session")
def roi_switzerland() -> shapely.geometry.base.BaseGeometry:
    """Return a ROI object for the bounds of Switzerland"""

    return BBox(
        latmin=45.81, lonmin=5.95, latmax=47.81, lonmax=10.5
    ).to_shapely()


@pytest.fixture(scope="session")
def resource_path_roi() -> str:
    """Return the path to the test ROI resources"""

    return os.path.join(os.getcwd(), "tests", "resources", "roi")


@pytest.fixture(scope="session")
def resource_path_query() -> str:
    """Return the path to the test query resources"""

    return os.path.join(os.getcwd(), "tests", "resources", "query")


@pytest.fixture
def nasa_stac_query_response(resource_path_query) -> OrderedDict:
    """Return a real response from NASA's STAC

    Query on:
        `earth-extractor batch --roi 45.81,5.95,47.81,10.5 --start 2022-11-19
          --end 2022-11-20 --satellite VIIRS:L1`
    """

    with open(
        os.path.join(
            resource_path_query,
            "nasa-stac-query-response.json",
        ),
        "r",
    ) as f:
        nasa_stac = f.read()

    return orjson.loads(nasa_stac)


@pytest.fixture(scope="session")
def scihub_query_response() -> OrderedDict:
    """Extract from the first three results of a query on Copernicus Data Space

    ```
    earth-extractor batch
        --roi 45.81,5.95,47.81,10.5
        --start 2016-11-19 --end 2016-12-29
        --satellite SENTINEL1:L1
    ```
    """

    return OrderedDict(
        {
            "@odata.context": "$metadata#Products(Assets())(Attributes())",
            "value": [
                {
                    "@odata.mediaContentType": "application/octet-stream",
                    "Id": "a07ea1c1-f46b-5e0a-9e8a-ffe11b1abc2d",
                    "Name": "S1A_IW_GRDH_1SDV_20161119T170709_20161119T170734_014014_01695F_0275.SAFE",
                    "ContentType": "application/octet-stream",
                    "ContentLength": 0,
                    "OriginDate": "2018-03-21T13:39:32.452Z",
                    "PublicationDate": "2018-12-17T03:25:33.980Z",
                    "ModificationDate": "2018-12-17T03:25:33.980Z",
                    "Online": True,
                    "EvictionDate": "",
                    "S3Path": "/eodata/Sentinel-1/SAR/GRD/2016/11/19/S1A_IW_GRDH_1SDV_20161119T170709_20161119T170734_014014_01695F_0275.SAFE",
                    "Checksum": [],
                    "ContentDate": {
                        "Start": "2016-11-19T17:07:09.166Z",
                        "End": "2016-11-19T17:07:34.164Z",
                    },
                    "Footprint": "geography'SRID=4326;POLYGON ((9.031395 48.417439, 12.509326 48.819859, 12.88131 47.325386, 9.502148 46.924618, 9.031395 48.417439))'",
                    "GeoFootprint": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [9.031395, 48.417439],
                                [12.509326, 48.819859],
                                [12.88131, 47.325386],
                                [9.502148, 46.924618],
                                [9.031395, 48.417439],
                            ]
                        ],
                    },
                    "Attributes": [
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "authority",
                            "Value": "ESA",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "timeliness",
                            "Value": "Fast-24h",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "coordinates",
                            "Value": "48.417439,9.031395 48.819859,12.509326 47.325386,12.881310 46.924618,9.502148 48.417439,9.031395",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.IntegerAttribute",
                            "Name": "orbitNumber",
                            "Value": 14014,
                            "ValueType": "Integer",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "productType",
                            "Value": "IW_GRDH_1S",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.IntegerAttribute",
                            "Name": "sliceNumber",
                            "Value": 11,
                            "ValueType": "Integer",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "productClass",
                            "Value": "S",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.DateTimeOffsetAttribute",
                            "Name": "endingDateTime",
                            "Value": "2016-11-19T17:07:34.164Z",
                            "ValueType": "DateTimeOffset",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "orbitDirection",
                            "Value": "ASCENDING",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "productGroupId",
                            "Value": 92511,
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "operationalMode",
                            "Value": "IW",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "processingLevel",
                            "Value": "LEVEL1",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "swathIdentifier",
                            "Value": "IW",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.DateTimeOffsetAttribute",
                            "Name": "beginningDateTime",
                            "Value": "2016-11-19T17:07:09.166Z",
                            "ValueType": "DateTimeOffset",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "platformShortName",
                            "Value": "SENTINEL-1",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.DoubleAttribute",
                            "Name": "spatialResolution",
                            "Value": 10.0,
                            "ValueType": "Double",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "instrumentShortName",
                            "Value": "SAR",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.IntegerAttribute",
                            "Name": "relativeOrbitNumber",
                            "Value": 117,
                            "ValueType": "Integer",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "polarisationChannels",
                            "Value": "VV&VH",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "platformSerialIdentifier",
                            "Value": "A",
                            "ValueType": "String",
                        },
                    ],
                    "Assets": [
                        {
                            "Type": "QUICKLOOK",
                            "Id": "4bdde11f-14a9-4544-841a-1fd221508c8e",
                            "DownloadLink": "https://catalogue.dataspace.copernicus.eu/odata/v1/Assets(4bdde11f-14a9-4544-841a-1fd221508c8e)/$value",
                            "S3Path": "/eodata/Sentinel-1/SAR/GRD/2016/11/19/S1A_IW_GRDH_1SDV_20161119T170709_20161119T170734_014014_01695F_0275.SAFE",
                        }
                    ],
                },
                {
                    "@odata.mediaContentType": "application/octet-stream",
                    "Id": "718ef996-52db-502d-85fb-7dc8d4b4ade5",
                    "Name": "S1A_IW_GRDH_1SDV_20161121T054245_20161121T054310_014036_016A10_DA15.SAFE",
                    "ContentType": "application/octet-stream",
                    "ContentLength": 0,
                    "OriginDate": "2019-02-16T03:15:45.220Z",
                    "PublicationDate": "2017-05-19T08:42:23.651Z",
                    "ModificationDate": "2017-05-19T08:42:23.651Z",
                    "Online": True,
                    "EvictionDate": "",
                    "S3Path": "/eodata/Sentinel-1/SAR/GRD/2016/11/21/S1A_IW_GRDH_1SDV_20161121T054245_20161121T054310_014036_016A10_DA15.SAFE",
                    "Checksum": [],
                    "ContentDate": {
                        "Start": "2016-11-21T05:42:45.388Z",
                        "End": "2016-11-21T05:43:10.385Z",
                    },
                    "Footprint": "geography'SRID=4326;POLYGON ((8.384936 47.165112, 4.939515 47.571758, 5.29238 49.067902, 8.839168 48.66016, 8.384936 47.165112))'",
                    "GeoFootprint": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [8.384936, 47.165112],
                                [4.939515, 47.571758],
                                [5.29238, 49.067902],
                                [8.839168, 48.66016],
                                [8.384936, 47.165112],
                            ]
                        ],
                    },
                    "Attributes": [
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "authority",
                            "Value": "ESA",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "timeliness",
                            "Value": "Fast-24h",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "coordinates",
                            "Value": "47.165112,8.384936 47.571758,4.939515 49.067902,5.292380 48.660160,8.839168 47.165112,8.384936",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.IntegerAttribute",
                            "Name": "orbitNumber",
                            "Value": 14036,
                            "ValueType": "Integer",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "productType",
                            "Value": "IW_GRDH_1S",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.IntegerAttribute",
                            "Name": "sliceNumber",
                            "Value": 18,
                            "ValueType": "Integer",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "productClass",
                            "Value": "S",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.DateTimeOffsetAttribute",
                            "Name": "endingDateTime",
                            "Value": "2016-11-21T05:43:10.385Z",
                            "ValueType": "DateTimeOffset",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "orbitDirection",
                            "Value": "DESCENDING",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "productGroupId",
                            "Value": 92688,
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "operationalMode",
                            "Value": "IW",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "processingLevel",
                            "Value": "LEVEL1",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "swathIdentifier",
                            "Value": "IW",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.DateTimeOffsetAttribute",
                            "Name": "beginningDateTime",
                            "Value": "2016-11-21T05:42:45.388Z",
                            "ValueType": "DateTimeOffset",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "platformShortName",
                            "Value": "SENTINEL-1",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.DoubleAttribute",
                            "Name": "spatialResolution",
                            "Value": 10.0,
                            "ValueType": "Double",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "instrumentShortName",
                            "Value": "SAR",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.IntegerAttribute",
                            "Name": "relativeOrbitNumber",
                            "Value": 139,
                            "ValueType": "Integer",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "polarisationChannels",
                            "Value": "VV&VH",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "platformSerialIdentifier",
                            "Value": "A",
                            "ValueType": "String",
                        },
                    ],
                    "Assets": [
                        {
                            "Type": "QUICKLOOK",
                            "Id": "1b120fe9-b71a-4721-9933-a13c67d7df77",
                            "DownloadLink": "https://catalogue.dataspace.copernicus.eu/odata/v1/Assets(1b120fe9-b71a-4721-9933-a13c67d7df77)/$value",
                            "S3Path": "/eodata/Sentinel-1/SAR/GRD/2016/11/21/S1A_IW_GRDH_1SDV_20161121T054245_20161121T054310_014036_016A10_DA15.SAFE",
                        }
                    ],
                },
                {
                    "@odata.mediaContentType": "application/octet-stream",
                    "Id": "d4f60153-18f3-55b3-ade1-f62f75f6f12a",
                    "Name": "S1A_IW_GRDH_1SDV_20161128T053501_20161128T053526_014138_016D3F_6808.SAFE",
                    "ContentType": "application/octet-stream",
                    "ContentLength": 0,
                    "OriginDate": "2019-02-19T08:51:24.810Z",
                    "PublicationDate": "2017-05-19T04:10:42.677Z",
                    "ModificationDate": "2017-05-19T04:10:42.677Z",
                    "Online": True,
                    "EvictionDate": "",
                    "S3Path": "/eodata/Sentinel-1/SAR/GRD/2016/11/28/S1A_IW_GRDH_1SDV_20161128T053501_20161128T053526_014138_016D3F_6808.SAFE",
                    "Checksum": [],
                    "ContentDate": {
                        "Start": "2016-11-28T05:35:01.280Z",
                        "End": "2016-11-28T05:35:26.280Z",
                    },
                    "Footprint": "geography'SRID=4326;POLYGON ((9.94106 45.379562, 6.607888 45.785946, 6.90909 47.287388, 10.334241 46.881863, 9.94106 45.379562))'",
                    "GeoFootprint": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [9.94106, 45.379562],
                                [6.607888, 45.785946],
                                [6.90909, 47.287388],
                                [10.334241, 46.881863],
                                [9.94106, 45.379562],
                            ]
                        ],
                    },
                    "Attributes": [
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "authority",
                            "Value": "ESA",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "timeliness",
                            "Value": "Fast-24h",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "coordinates",
                            "Value": "45.379562,9.941060 45.785946,6.607888 47.287388,6.909090 46.881863,10.334241 45.379562,9.941060",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.IntegerAttribute",
                            "Name": "orbitNumber",
                            "Value": 14138,
                            "ValueType": "Integer",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "productType",
                            "Value": "IW_GRDH_1S",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.IntegerAttribute",
                            "Name": "sliceNumber",
                            "Value": 19,
                            "ValueType": "Integer",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "productClass",
                            "Value": "S",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.DateTimeOffsetAttribute",
                            "Name": "endingDateTime",
                            "Value": "2016-11-28T05:35:26.280Z",
                            "ValueType": "DateTimeOffset",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "orbitDirection",
                            "Value": "DESCENDING",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "productGroupId",
                            "Value": 93503,
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "operationalMode",
                            "Value": "IW",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "processingLevel",
                            "Value": "LEVEL1",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "swathIdentifier",
                            "Value": "IW",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.DateTimeOffsetAttribute",
                            "Name": "beginningDateTime",
                            "Value": "2016-11-28T05:35:01.280Z",
                            "ValueType": "DateTimeOffset",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "platformShortName",
                            "Value": "SENTINEL-1",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.DoubleAttribute",
                            "Name": "spatialResolution",
                            "Value": 10.0,
                            "ValueType": "Double",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "instrumentShortName",
                            "Value": "SAR",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.IntegerAttribute",
                            "Name": "relativeOrbitNumber",
                            "Value": 66,
                            "ValueType": "Integer",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "polarisationChannels",
                            "Value": "VV&VH",
                            "ValueType": "String",
                        },
                        {
                            "@odata.type": "#OData.CSC.StringAttribute",
                            "Name": "platformSerialIdentifier",
                            "Value": "A",
                            "ValueType": "String",
                        },
                    ],
                    "Assets": [
                        {
                            "Type": "QUICKLOOK",
                            "Id": "4b3e023e-1664-491d-b292-770bbb42e499",
                            "DownloadLink": "https://catalogue.dataspace.copernicus.eu/odata/v1/Assets(4b3e023e-1664-491d-b292-770bbb42e499)/$value",
                            "S3Path": "/eodata/Sentinel-1/SAR/GRD/2016/11/28/S1A_IW_GRDH_1SDV_20161128T053501_20161128T053526_014138_016D3F_6808.SAFE",
                        }
                    ],
                },
            ],
        }
    )


@pytest.fixture(scope="session")
def sentinel_query_as_commonsearch_result(
    scihub_query_response: OrderedDict,
) -> List[CommonSearchResult]:
    """A file id for downloading from the ASF API"""

    return copernicus_dataspace.translate_search_results(scihub_query_response)


@pytest.fixture
def swisstopo_query_response() -> List[CommonSearchResult]:
    """ Return a list of results from a query

    Query on:
    ```
        earth-extractor batch \
            --start 2020-10-06 --end 2023-01-01 \
            --roi 7.35999,46.22457 --buffer 200 \
            --satellite swissimage:cm200 \
            --satellite swissimage:cm10 \
            --no-confirmation
    ```
    """
    return [
        CommonSearchResult(
            satellite=Satellite.SWISSIMAGE,
            product_id=None,
            link=None,
            identifier=None,
            filename=None,
            time=None,
            cloud_cover_percentage=None,
            size=None,
            processing_level=ProcessingLevel.CM200,
            sensor=None,
            geometry="POLYGON ((7.361786630568239 46.22456999999999, 7.361777979300983 46.22444816755935, 7.361752108815652 46.22432750816523, 7.361709268259157 46.224209183845076, 7.361649870209481 46.22409433414552, 7.361574486702308 46.223984065157126, 7.361483843722025 46.223879438861246, 7.36137881421008 46.22378146290134, 7.361260409658089 46.22369108087745, 7.361129770366614 46.223609163257436, 7.360988154463446 46.22353649899225, 7.360836925787149 46.22347378791654, 7.360677540752547 46.223421634007245, 7.3605115343246466 46.22338053956574, 7.360340505236103 46.22335090037915, 7.360166100590527 46.2233330019078, 7.359990000000001 46.22332701653524, 7.359813899409473 46.2233330019078, 7.359639494763899 46.22335090037915, 7.359468465675353 46.22338053956574, 7.359302459247454 46.223421634007245, 7.35914307421285 46.22347378791654, 7.358991845536554 46.22353649899225, 7.3588502296333855 46.223609163257436, 7.358719590341912 46.22369108087745, 7.35860118578992 46.22378146290134, 7.358496156277975 46.223879438861246, 7.358405513297692 46.223984065157126, 7.35833012979052 46.22409433414552, 7.358270731740842 46.224209183845076, 7.358227891184348 46.22432750816523, 7.358202020699016 46.22444816755935, 7.358193369431761 46.22456999999999, 7.358202020699016 46.22469183217025, 7.358227891184348 46.224812490763625, 7.358270731740842 46.224930813783445, 7.35833012979052 46.22504566173304, 7.358405513297692 46.225155928589096, 7.358496156277975 46.22526055245221, 7.35860118578992 46.22535852577243, 7.358719590341912 46.2254489050511, 7.3588502296333855 46.22553081992593, 7.358991845536554 46.2256034815514, 7.35914307421285 46.22566619019436, 7.359302459247454 46.225718341971316, 7.359468465675353 46.225759434662855, 7.359639494763899 46.225789072549105, 7.359813899409473 46.22580697021972, 7.359990000000001 46.22581295532189, 7.360166100590527 46.22580697021972, 7.360340505236103 46.225789072549105, 7.3605115343246466 46.225759434662855, 7.360677540752547 46.225718341971316, 7.360836925787149 46.22566619019436, 7.360988154463446 46.2256034815514, 7.361129770366614 46.22553081992593, 7.361260409658089 46.2254489050511, 7.36137881421008 46.22535852577243, 7.361483843722025 46.22526055245221, 7.361574486702308 46.225155928589096, 7.361649870209481 46.22504566173304, 7.361709268259157 46.224930813783445, 7.361752108815652 46.224812490763625, 7.361777979300983 46.22469183217025, 7.361786630568239 46.22456999999999))",
            url="https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2593-1119/swissimage-dop10_2020_2593-1119_2_2056.tif",
            notes="SwissImage geometry reflects only the given ROI, not the actual boundary of the image. See comments within the code for more information.",
        ),
        CommonSearchResult(
            satellite=Satellite.SWISSIMAGE,
            product_id=None,
            link=None,
            identifier=None,
            filename=None,
            time=None,
            cloud_cover_percentage=None,
            size=None,
            processing_level=ProcessingLevel.CM200,
            sensor=None,
            geometry="POLYGON ((7.361786630568239 46.22456999999999, 7.361777979300983 46.22444816755935, 7.361752108815652 46.22432750816523, 7.361709268259157 46.224209183845076, 7.361649870209481 46.22409433414552, 7.361574486702308 46.223984065157126, 7.361483843722025 46.223879438861246, 7.36137881421008 46.22378146290134, 7.361260409658089 46.22369108087745, 7.361129770366614 46.223609163257436, 7.360988154463446 46.22353649899225, 7.360836925787149 46.22347378791654, 7.360677540752547 46.223421634007245, 7.3605115343246466 46.22338053956574, 7.360340505236103 46.22335090037915, 7.360166100590527 46.2233330019078, 7.359990000000001 46.22332701653524, 7.359813899409473 46.2233330019078, 7.359639494763899 46.22335090037915, 7.359468465675353 46.22338053956574, 7.359302459247454 46.223421634007245, 7.35914307421285 46.22347378791654, 7.358991845536554 46.22353649899225, 7.3588502296333855 46.223609163257436, 7.358719590341912 46.22369108087745, 7.35860118578992 46.22378146290134, 7.358496156277975 46.223879438861246, 7.358405513297692 46.223984065157126, 7.35833012979052 46.22409433414552, 7.358270731740842 46.224209183845076, 7.358227891184348 46.22432750816523, 7.358202020699016 46.22444816755935, 7.358193369431761 46.22456999999999, 7.358202020699016 46.22469183217025, 7.358227891184348 46.224812490763625, 7.358270731740842 46.224930813783445, 7.35833012979052 46.22504566173304, 7.358405513297692 46.225155928589096, 7.358496156277975 46.22526055245221, 7.35860118578992 46.22535852577243, 7.358719590341912 46.2254489050511, 7.3588502296333855 46.22553081992593, 7.358991845536554 46.2256034815514, 7.35914307421285 46.22566619019436, 7.359302459247454 46.225718341971316, 7.359468465675353 46.225759434662855, 7.359639494763899 46.225789072549105, 7.359813899409473 46.22580697021972, 7.359990000000001 46.22581295532189, 7.360166100590527 46.22580697021972, 7.360340505236103 46.225789072549105, 7.3605115343246466 46.225759434662855, 7.360677540752547 46.225718341971316, 7.360836925787149 46.22566619019436, 7.360988154463446 46.2256034815514, 7.361129770366614 46.22553081992593, 7.361260409658089 46.2254489050511, 7.36137881421008 46.22535852577243, 7.361483843722025 46.22526055245221, 7.361574486702308 46.225155928589096, 7.361649870209481 46.22504566173304, 7.361709268259157 46.224930813783445, 7.361752108815652 46.224812490763625, 7.361777979300983 46.22469183217025, 7.361786630568239 46.22456999999999))",
            url="https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2594-1119/swissimage-dop10_2020_2594-1119_2_2056.tif",
            notes="SwissImage geometry reflects only the given ROI, not the actual boundary of the image. See comments within the code for more information.",
        ),
    ]
