# flake8: noqa
import pytest
from earth_extractor.core.models import BBox, CommonSearchResult
from earth_extractor.core.credentials import Credentials
from earth_extractor.satellites.enums import Satellite, ProcessingLevel
from earth_extractor.providers import copernicus_scihub
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
    """Extract from the first three results of:

    from datetime import datetime
    from earth_extractor.core.models import BBox

    roi = BBox(
        latmin=45.81, lonmin=5.95, latmax=47.81, lonmax=10.5
    ).to_shapely().wkt
    res = api.query(
        roi,
        producttype='GRD',
        date=(datetime(2016, 11, 19), datetime(2016, 12, 29)),
    )
    """

    return OrderedDict(
        [
            (
                "1caf27cb-517b-4297-812d-00771c5ffe91",
                {
                    "title": "S1B_IW_GRDH_1SDV_20161120T055018_20161120T055043_003038_0052A6_1F5B",
                    "link": "https://apihub.copernicus.eu/apihub/odata/v1/Products('1caf27cb-517b-4297-812d-00771c5ffe91')/$value",
                    "link_alternative": "https://apihub.copernicus.eu/apihub/odata/v1/Products('1caf27cb-517b-4297-812d-00771c5ffe91')/",
                    "link_icon": "https://apihub.copernicus.eu/apihub/odata/v1/Products('1caf27cb-517b-4297-812d-00771c5ffe91')/Products('Quicklook')/$value",
                    "summary": "Date: 2016-11-20T05:50:18.699Z, Instrument: SAR-C SAR, Mode: VV VH, Satellite: Sentinel-1, Size: 1.66 GB",
                    "ondemand": "false",
                    "ingestiondate": datetime.datetime(
                        2018, 3, 28, 23, 8, 54, 662000
                    ),
                    "beginposition": datetime.datetime(
                        2016, 11, 20, 5, 50, 18, 699000
                    ),
                    "endposition": datetime.datetime(
                        2016, 11, 20, 5, 50, 43, 696000
                    ),
                    "missiondatatakeid": 21158,
                    "orbitnumber": 3038,
                    "lastorbitnumber": 3038,
                    "relativeorbitnumber": 37,
                    "lastrelativeorbitnumber": 37,
                    "slicenumber": 18,
                    "acquisitiontype": "NOMINAL",
                    "filename": "S1B_IW_GRDH_1SDV_20161120T055018_20161120T055043_003038_0052A6_1F5B.SAFE",
                    "gmlfootprint": '<gml:Polygon srsName="http://www.opengis.net/gml/srs/epsg.xml#4326" xmlns:gml="http://www.opengis.net/gml">\n   <gml:outerBoundaryIs>\n      <gml:LinearRing>\n         <gml:coordinates>47.054276,6.332564 47.465588,2.859072 48.962429,3.204872 48.550240,6.780112 47.054276,6.332564</gml:coordinates>\n      </gml:LinearRing>\n   </gml:outerBoundaryIs>\n</gml:Polygon>',
                    "format": "SAFE",
                    "identifier": "S1B_IW_GRDH_1SDV_20161120T055018_20161120T055043_003038_0052A6_1F5B",
                    "instrumentshortname": "SAR-C SAR",
                    "sensoroperationalmode": "IW",
                    "instrumentname": "Synthetic Aperture Radar (C-band)",
                    "swathidentifier": "IW",
                    "footprint": "POLYGON ((6.332564 47.054276,2.859072 47.465588,3.204872 48.962429,6.780112 48.550240,6.332564 47.054276))",
                    "platformidentifier": "2016-025A",
                    "orbitdirection": "DESCENDING",
                    "polarisationmode": "VV VH",
                    "productclass": "S",
                    "producttype": "GRD",
                    "platformname": "Sentinel-1",
                    "size": "1.66 GB",
                    "status": "ARCHIVED",
                    "uuid": "1caf27cb-517b-4297-812d-00771c5ffe91",
                },
            ),
            (
                "ac19afe0-a237-4786-b391-e61f903f936f",
                {
                    "title": "S1B_EW_GRDM_1SDH_20161120T165800_20161120T165904_003045_0052D1_B6EE",
                    "link": "https://apihub.copernicus.eu/apihub/odata/v1/Products('ac19afe0-a237-4786-b391-e61f903f936f')/$value",
                    "link_alternative": "https://apihub.copernicus.eu/apihub/odata/v1/Products('ac19afe0-a237-4786-b391-e61f903f936f')/",
                    "link_icon": "https://apihub.copernicus.eu/apihub/odata/v1/Products('ac19afe0-a237-4786-b391-e61f903f936f')/Products('Quicklook')/$value",
                    "summary": "Date: 2016-11-20T16:58:00.344Z, Instrument: SAR-C SAR, Mode: HH HV, Satellite: Sentinel-1, Size: 448.23 MB",
                    "ondemand": "false",
                    "ingestiondate": datetime.datetime(
                        2018, 3, 28, 11, 48, 52, 208000
                    ),
                    "beginposition": datetime.datetime(
                        2016, 11, 20, 16, 58, 0, 344000
                    ),
                    "endposition": datetime.datetime(
                        2016, 11, 20, 16, 59, 4, 621000
                    ),
                    "missiondatatakeid": 21201,
                    "orbitnumber": 3045,
                    "lastorbitnumber": 3045,
                    "relativeorbitnumber": 44,
                    "lastrelativeorbitnumber": 44,
                    "slicenumber": 1,
                    "acquisitiontype": "NOMINAL",
                    "filename": "S1B_EW_GRDM_1SDH_20161120T165800_20161120T165904_003045_0052D1_B6EE.SAFE",
                    "gmlfootprint": '<gml:Polygon srsName="http://www.opengis.net/gml/srs/epsg.xml#4326" xmlns:gml="http://www.opengis.net/gml">\n   <gml:outerBoundaryIs>\n      <gml:LinearRing>\n         <gml:coordinates>49.730785,8.698680 50.435776,14.603304 46.593281,15.527373 45.900047,10.045737 49.730785,8.698680</gml:coordinates>\n      </gml:LinearRing>\n   </gml:outerBoundaryIs>\n</gml:Polygon>',
                    "format": "SAFE",
                    "identifier": "S1B_EW_GRDM_1SDH_20161120T165800_20161120T165904_003045_0052D1_B6EE",
                    "instrumentshortname": "SAR-C SAR",
                    "sensoroperationalmode": "EW",
                    "instrumentname": "Synthetic Aperture Radar (C-band)",
                    "swathidentifier": "EW",
                    "footprint": "POLYGON ((8.698680 49.730785,14.603304 50.435776,15.527373 46.593281,10.045737 45.900047,8.698680 49.730785))",
                    "platformidentifier": "2016-025A",
                    "orbitdirection": "ASCENDING",
                    "polarisationmode": "HH HV",
                    "productclass": "S",
                    "producttype": "GRD",
                    "platformname": "Sentinel-1",
                    "size": "448.23 MB",
                    "status": "ARCHIVED",
                    "uuid": "ac19afe0-a237-4786-b391-e61f903f936f",
                },
            ),
            (
                "ca2663c6-d853-4452-86f3-618bfc295c3b",
                {
                    "title": "S1A_IW_GRDH_1SDV_20161119T170644_20161119T170709_014014_01695F_4196",
                    "link": "https://apihub.copernicus.eu/apihub/odata/v1/Products('ca2663c6-d853-4452-86f3-618bfc295c3b')/$value",
                    "link_alternative": "https://apihub.copernicus.eu/apihub/odata/v1/Products('ca2663c6-d853-4452-86f3-618bfc295c3b')/",
                    "link_icon": "https://apihub.copernicus.eu/apihub/odata/v1/Products('ca2663c6-d853-4452-86f3-618bfc295c3b')/Products('Quicklook')/$value",
                    "summary": "Date: 2016-11-19T17:06:44.165Z, Instrument: SAR-C SAR, Mode: VV VH, Satellite: Sentinel-1, Size: 1.62 GB",
                    "ondemand": "false",
                    "ingestiondate": datetime.datetime(
                        2018, 3, 21, 13, 29, 21, 192000
                    ),
                    "beginposition": datetime.datetime(
                        2016, 11, 19, 17, 6, 44, 165000
                    ),
                    "endposition": datetime.datetime(
                        2016, 11, 19, 17, 7, 9, 164000
                    ),
                    "missiondatatakeid": 92511,
                    "orbitnumber": 14014,
                    "lastorbitnumber": 14014,
                    "relativeorbitnumber": 117,
                    "lastrelativeorbitnumber": 117,
                    "slicenumber": 10,
                    "acquisitiontype": "NOMINAL",
                    "filename": "S1A_IW_GRDH_1SDV_20161119T170644_20161119T170709_014014_01695F_4196.SAFE",
                    "gmlfootprint": '<gml:Polygon srsName="http://www.opengis.net/gml/srs/epsg.xml#4326" xmlns:gml="http://www.opengis.net/gml">\n   <gml:outerBoundaryIs>\n      <gml:LinearRing>\n         <gml:coordinates>46.924530,9.502173 47.325146,12.879891 45.823727,13.183452 45.422325,9.896425 46.924530,9.502173</gml:coordinates>\n      </gml:LinearRing>\n   </gml:outerBoundaryIs>\n</gml:Polygon>',
                    "format": "SAFE",
                    "identifier": "S1A_IW_GRDH_1SDV_20161119T170644_20161119T170709_014014_01695F_4196",
                    "instrumentshortname": "SAR-C SAR",
                    "sensoroperationalmode": "IW",
                    "instrumentname": "Synthetic Aperture Radar (C-band)",
                    "swathidentifier": "IW",
                    "footprint": "POLYGON ((9.502173 46.924530,12.879891 47.325146,13.183452 45.823727,9.896425 45.422325,9.502173 46.924530))",
                    "platformidentifier": "2014-016A",
                    "orbitdirection": "ASCENDING",
                    "polarisationmode": "VV VH",
                    "productclass": "S",
                    "producttype": "GRD",
                    "platformname": "Sentinel-1",
                    "size": "1.62 GB",
                    "status": "ARCHIVED",
                    "uuid": "ca2663c6-d853-4452-86f3-618bfc295c3b",
                },
            ),
        ]
    )


@pytest.fixture(scope="session")
def sentinel_query_as_commonsearch_result(
    scihub_query_response: OrderedDict,
) -> List[CommonSearchResult]:
    """A file id for downloading from the ASF API"""

    return copernicus_scihub.translate_search_results(scihub_query_response)


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
