# Earth Extractor

Earth Extractor simplifies the workflow of data acquisition from multiple
satellite data providers. The library is designed to be used as a command line
tool, but can also be used as a library.

Unlike other projects, Earth Extractor is designed to simplify the data
acquisition process for a select amount of satellite providers and is
deliberately written to provide a hands-off approach for simple data
collection. This is dissimilar to projects
such as [EODag](https://github.com/CS-SI/eodag) and
[getSpatialData](https://github.com/16EAGLE/getSpatialData) which aim to
harmonise the process over many providers and satellite types.

The library creates a framework around providers and satellites, allowing
a satellite to have separate providers for querying and downloading. This
provides the benefit of searching with an API allowing more comprehensive
filters than those that are available in the download provider. For example,
the Copernicus Open Access Hub allows cloud coverage filters, but the data is
better served by the Alaskan Satellite Facility which does not offer such
filters.

### Changelog
Semantic version changes are tracked in the [CHANGELOG](./CHANGELOG.md).

# Getting started
## Installation

### Install from PyPI

In your local environment, install the package with:

```bash
pip install earth-extractor
```

The package repository can be found at
[PyPI: earth-extractor](https://pypi.org/project/earth-extractor/).

### Install from git (development)

If poetry is not installed locally, install it first with:

```bash
pip install poetry
```

Then clone the repository and install the package dependencies with:

```bash
git clone https://github.com/eceo-epfl/earth-extractor
cd earth-extractor
poetry install
```

### Define user credentials

There are two methods to store the provider secrets required to access the
data:

1. [System keyring (recommended)](#option-1-system-keyring-recommended)
2. [.env file](#option-2-env-file)

#### Option 1: System keyring (recommended)

This method requires that your operating system has a secret keyring installed.
This is usually the case, but if you're operating a server linux installation,
or using WSL on Windows, for example, one may not exist. In this case, you can
use the `.env` file method.

User credentials are managed by the `keyring` library which make use of your
operating system's secret keyring. The credentials are stored in the system
and are retrieved by the library when required.

In order to define them, use the following command:

```bash
earth-extractor credentials --set
```

#### Option 2: .env file

In the folder you are working in, place an .env file with the keys and values
as follows (the necessary keys can be found in the [credential sources](#credential-sources) section underneath):

```bash
SCIHUB_USERNAME=
SCIHUB_PASSWORD=
NASA_TOKEN=
```

# Credential sources

Credentials can be obtained from the respective providers:
* [Copernicus Open Access Hub](https://scihub.copernicus.eu/dhus/#/self-registration)
    * `SCIHUB_USERNAME` and `SCIHUB_PASSWORD`


* [Alaskan Satellite Facility](https://asf.alaska.edu/) and [NASA LAADS repository](https://ladsweb.modaps.eosdis.nasa.gov/)
    * `NASA_TOKEN`
    * Obtain the token by registering first at [NASA EarthData](https://urs.earthdata.nasa.gov/users/new), and then in `My Profile`, select `Generate Token` from the top menu and
    `GENERATE TOKEN` from the bottom of the page.
    * Make sure to accept the Alaskan Satellite Facility EULA after registering
    in [NASA Earth Data: Accept New EULAs](https://urs.earthdata.nasa.gov/users/ejayt/unaccepted_eulas)

## Example usage (CLI)

### Sentinel 1
Search for `Sentinel-1 L1` data for Switzerland between the dates
`2022-11-19` and `2022-11-29`.

```bash
earth-extractor batch \
    --roi 45.81,5.95,47.81,10.5 \
    --start 2022-11-19 --end 2022-11-29 \
    --satellite SENTINEL1:L1
```

### SwissImage

Search and download `SwissImage` `0.1m` and `2.0m` resolution data for a
`200 metre` buffered region around longitude: `7.35999°` and latitude:
`46.22457°` between the dates `2022-11-19` and `2022-11-29`.

Note: In this example the download will start without user intervention, by
using the `--no-confirmation` flag. We can also see the first use of multiple
satellites in the same query (although SwissImage is not technically a
"satellite" product).

```bash
earth-extractor batch \
    --start 2020-10-06 --end 2023-01-01 \
    --roi 7.35999,46.22457 --buffer 200 \
    --satellite swissimage:cm200 \
    --satellite swissimage:cm10 \
    --no-confirmation
```

### MODIS and VIIRS

Search for VIIRS (L1) and MODIS Terra (L1B) data with a `2km` buffered region
around longitude: `7.35999°` and latitude: `46.22457°` between the dates
`2022-10-06` and `2023-01-01`.

```bash
earth-extractor batch \
    --start 2022-10-06 --end 2022-10-07 \
    --roi 7.35999,46.22457 --buffer 2000 \
    --satellite VIIRS:L1 \
    --satellite MODIS_TERRA:L1B \
    --no-confirmation
```

# Technical specifications

## Components
### Satellites and providers
The following satellites and respective processing levels are
included in the design:


| **Satellite** | **Levels**            | **Search provider**               | **Download provider**             |
|---------------|-----------------------|-----------------------------------|-----------------------------------|
| **Sentinel-1**| 1 (GRD)               | SCIHUB                            | Alaskan Satellite Facility        |
|               | 2 (GRD_SIGMA0)        | SCIHUB                            | SCIHUB                            |
| **Sentinel-2**| 1C                    | SCIHUB                            | SCIHUB                            |
|               | 2A                    | SCIHUB                            | SCIHUB                            |
| **Sentinel-3**| 1B                    | SCIHUB                            | SCIHUB                            |
|               | 2                     | SCIHUB                            | SCIHUB                            |
|               | 3 LFR Atmos (Land)    | SCIHUB                            | SCIHUB                            |
|               | 3 WFR Atmos (Water)   | SCIHUB                            | SCIHUB                            |
| **MODIS Terra**| 1B                   | NASA Common Metadata Repository   | NASA LAADS                        |
| **MODIS Aqua** | 1B                   | NASA Common Metadata Repository   | NASA LAADS                        |
| **VIIRS**      | 1                    | NASA Common Metadata Repository   | NASA LAADS                        |
