"""End-to-end tests against live APIs.

These tests require real credentials to be configured via the keyring
or a .env file. They are skipped automatically when credentials are
not set.

Run with:
    uv run pytest tests/e2e/ -v
"""

import os
import pytest
import shapely.geometry
from datetime import datetime

import keyring
import keyring.backends
from keyring.errors import KeyringError

# Override the null keyring backend set by pyproject.toml [tool.pytest.ini_options]
# so e2e tests can access real credentials from the system keyring.
try:
    from keyring.backends import SecretService
    keyring.set_keyring(SecretService.Keyring())
except Exception:
    pass

KEYRING_ID = "earth-extractor"


def _get_keyring_value(key: str) -> str | None:
    try:
        return keyring.get_password(KEYRING_ID, key)
    except KeyringError:
        return None


_copernicus_user = _get_keyring_value("COPERNICUS_USERNAME")
_copernicus_pass = _get_keyring_value("COPERNICUS_PASSWORD")
_nasa_token = _get_keyring_value("NASA_TOKEN")

has_copernicus = _copernicus_user is not None and _copernicus_pass is not None
has_nasa = _nasa_token is not None

# Set env vars so the Credentials model reads real values, then clear the
# lru_cache and refresh the module-level credential references used by
# providers during download.
if has_copernicus:
    os.environ["COPERNICUS_USERNAME"] = _copernicus_user
    os.environ["COPERNICUS_PASSWORD"] = _copernicus_pass
if has_nasa:
    os.environ["NASA_TOKEN"] = _nasa_token

if has_copernicus or has_nasa:
    from earth_extractor.core.credentials import get_credentials
    get_credentials.cache_clear()
    _real_creds = get_credentials()
    # Refresh module-level credential references in providers
    import earth_extractor.providers.copernicus as _cop_mod
    import earth_extractor.providers.nasa as _nasa_mod
    _cop_mod.credentials = _real_creds
    _nasa_mod.credentials = _real_creds

requires_copernicus = pytest.mark.skipif(
    not has_copernicus,
    reason="COPERNICUS_USERNAME / COPERNICUS_PASSWORD not set",
)
requires_nasa = pytest.mark.skipif(
    not has_nasa,
    reason="NASA_TOKEN not set",
)


# --- Fixtures ---

@pytest.fixture
def small_roi() -> shapely.geometry.Polygon:
    """Small bounding box near Lausanne, Switzerland."""
    return shapely.geometry.box(6.6, 46.5, 6.7, 46.6)


@pytest.fixture
def small_swiss_roi() -> shapely.geometry.Polygon:
    """Tiny area near EPFL for SwissTopo tests."""
    return shapely.geometry.box(6.62, 46.51, 6.64, 46.53)


# =============================================================================
# Copernicus Data Space
# =============================================================================

class TestCopernicus:

    @requires_copernicus
    def test_auth(self):
        """Validate Copernicus credentials by obtaining an access token."""
        from earth_extractor.providers.copernicus import copernicus_dataspace

        token = copernicus_dataspace.get_access_token(
            _copernicus_user, _copernicus_pass
        )
        assert isinstance(token, str)
        assert len(token) > 50

    @requires_copernicus
    def test_sentinel2_query(self, small_roi):
        """Query Sentinel-2 L2A products from Copernicus."""
        from earth_extractor.providers.copernicus import copernicus_dataspace
        from earth_extractor.satellites.sentinel import sentinel_2
        from earth_extractor.satellites.enums import ProcessingLevel

        results = copernicus_dataspace.query(
            satellite=sentinel_2,
            processing_level=ProcessingLevel.L2A,
            roi=small_roi,
            start_date=datetime(2024, 6, 1),
            end_date=datetime(2024, 6, 15),
            cloud_cover=80,
        )
        assert len(results) > 0
        for r in results:
            assert r.url is not None
            assert r.geometry is not None
            assert r.satellite is not None

    @requires_copernicus
    def test_sentinel1_query(self, small_roi):
        """Query Sentinel-1 L1 products from Copernicus."""
        from earth_extractor.providers.copernicus import copernicus_dataspace
        from earth_extractor.satellites.sentinel import sentinel_1
        from earth_extractor.satellites.enums import ProcessingLevel

        results = copernicus_dataspace.query(
            satellite=sentinel_1,
            processing_level=ProcessingLevel.L1,
            roi=small_roi,
            start_date=datetime(2024, 6, 1),
            end_date=datetime(2024, 6, 15),
        )
        assert len(results) > 0

    @requires_copernicus
    def test_sentinel2_download(self, small_roi, tmp_path):
        """Download a single small Sentinel-2 product."""
        from earth_extractor.providers.copernicus import copernicus_dataspace
        from earth_extractor.satellites.sentinel import sentinel_2
        from earth_extractor.satellites.enums import ProcessingLevel

        results = copernicus_dataspace.query(
            satellite=sentinel_2,
            processing_level=ProcessingLevel.L2A,
            roi=small_roi,
            start_date=datetime(2024, 6, 1),
            end_date=datetime(2024, 6, 15),
            cloud_cover=80,
        )
        assert len(results) > 0

        copernicus_dataspace.download_many(
            search_results=results[:1],
            download_dir=str(tmp_path),
        )
        downloaded = list(tmp_path.iterdir())
        # Filter out log files
        data_files = [f for f in downloaded if not f.suffix == ".log"]
        assert len(data_files) >= 1
        assert all(f.stat().st_size > 0 for f in data_files)


# =============================================================================
# NASA CMR (MODIS / VIIRS)
# =============================================================================

class TestNASA:

    @requires_nasa
    def test_modis_terra_query(self, small_roi):
        """Query MODIS Terra L1B products from NASA CMR."""
        from earth_extractor.providers.nasa import nasa_cmr
        from earth_extractor.satellites.modis import modis_terra
        from earth_extractor.satellites.enums import ProcessingLevel

        results = nasa_cmr.query(
            satellite=modis_terra,
            processing_level=ProcessingLevel.L1B,
            roi=small_roi,
            start_date=datetime(2024, 6, 1),
            end_date=datetime(2024, 6, 2),
        )
        assert len(results) > 0
        for r in results:
            assert r.url is not None
            assert r.product_id is not None
            assert "LAADS:" in r.product_id

    @requires_nasa
    def test_modis_aqua_query(self, small_roi):
        """Query MODIS Aqua L1B products from NASA CMR."""
        from earth_extractor.providers.nasa import nasa_cmr
        from earth_extractor.satellites.modis import modis_aqua
        from earth_extractor.satellites.enums import ProcessingLevel

        results = nasa_cmr.query(
            satellite=modis_aqua,
            processing_level=ProcessingLevel.L1B,
            roi=small_roi,
            start_date=datetime(2024, 6, 1),
            end_date=datetime(2024, 6, 2),
        )
        assert len(results) > 0

    @requires_nasa
    def test_viirs_query(self, small_roi):
        """Query VIIRS L1 products from NASA CMR."""
        from earth_extractor.providers.nasa import nasa_cmr
        from earth_extractor.satellites.viirs import viirs
        from earth_extractor.satellites.enums import ProcessingLevel

        results = nasa_cmr.query(
            satellite=viirs,
            processing_level=ProcessingLevel.L1,
            roi=small_roi,
            start_date=datetime(2024, 6, 1),
            end_date=datetime(2024, 6, 2),
        )
        assert len(results) > 0

    @requires_nasa
    def test_modis_download(self, small_roi, tmp_path):
        """Download a single MODIS file from NASA."""
        from earth_extractor.providers.nasa import nasa_cmr
        from earth_extractor.satellites.modis import modis_terra
        from earth_extractor.satellites.enums import ProcessingLevel

        results = nasa_cmr.query(
            satellite=modis_terra,
            processing_level=ProcessingLevel.L1B,
            roi=small_roi,
            start_date=datetime(2024, 6, 1),
            end_date=datetime(2024, 6, 2),
        )
        assert len(results) > 0

        nasa_cmr.download_many(
            search_results=results[:1],
            download_dir=str(tmp_path),
        )
        downloaded = list(tmp_path.iterdir())
        assert len(downloaded) >= 1
        assert all(f.stat().st_size > 0 for f in downloaded)


# =============================================================================
# SwissTopo (no credentials needed)
# =============================================================================

class TestSwissTopo:

    def test_swissimage_10cm_query(self, small_swiss_roi):
        """Query SWISSIMAGE 10cm tiles from SwissTopo STAC."""
        from earth_extractor.providers.swisstopo import swiss_topo
        from earth_extractor.satellites.swissimage import swissimage
        from earth_extractor.satellites.enums import ProcessingLevel

        results = swiss_topo.query(
            satellite=swissimage,
            processing_level=ProcessingLevel.CM10,
            roi=small_swiss_roi,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2024, 12, 31),
        )
        assert len(results) > 0
        for r in results:
            assert r.url is not None
            assert "data.geo.admin.ch" in r.url
            assert r.geometry is not None
            assert r.identifier is not None

    def test_swissimage_200cm_query(self, small_swiss_roi):
        """Query SWISSIMAGE 2m tiles from SwissTopo STAC."""
        from earth_extractor.providers.swisstopo import swiss_topo
        from earth_extractor.satellites.swissimage import swissimage
        from earth_extractor.satellites.enums import ProcessingLevel

        results = swiss_topo.query(
            satellite=swissimage,
            processing_level=ProcessingLevel.CM200,
            roi=small_swiss_roi,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2024, 12, 31),
        )
        assert len(results) > 0

    def test_swissimage_download(self, small_swiss_roi, tmp_path):
        """Download a SWISSIMAGE 2m tile (small, ~200KB)."""
        from earth_extractor.providers.swisstopo import swiss_topo
        from earth_extractor.satellites.swissimage import swissimage
        from earth_extractor.satellites.enums import ProcessingLevel

        results = swiss_topo.query(
            satellite=swissimage,
            processing_level=ProcessingLevel.CM200,
            roi=small_swiss_roi,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2024, 12, 31),
        )
        assert len(results) > 0

        swiss_topo.download_many(
            search_results=results[:1],
            download_dir=str(tmp_path),
        )
        downloaded = list(tmp_path.glob("*.tif"))
        assert len(downloaded) == 1
        assert downloaded[0].stat().st_size > 1000
