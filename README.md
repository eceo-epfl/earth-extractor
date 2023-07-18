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

### Install from git

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

User credentials are managed by the `keyring` library which make use of your
operating system's secret keyring. The credentials are stored in the system
and are retrieved by the library when required.

In order to define them, use the following command:

```bash
poetry run earth-extractor credentials --set
```

Credentials can be obtained from the respective providers:
* [Copernicus Open Access Hub](https://scihub.copernicus.eu/dhus/#/self-registration)
    * `SCIHUB_USERNAME` and `SCIHUB_PASSWORD`

* [Alaskan Satellite Facility](https://urs.earthdata.nasa.gov/users/new)
    * `NASA_USERNAME` and `NASA_PASSWORD`

* [Sinergise](https://www.sentinel-hub.com)
    * `SINERGISE_CLIENT_ID` and `SINERGISE_CLIENT_SECRET`
    * At the moment this is unused
    * Obtain an [OAuth2 Client ID and Secret](https://docs.sentinel-hub.com/api/latest/api/overview/authentication/)
    from the [user dashboard](https://apps.sentinel-hub.com/dashboard/#/account/settings)


## Example usage (CLI)

Search for Sentinel-1 L2 data for Switzerland between the dates
2022-11-19 and 2022-11-29.

```bash
poetry run earth-extractor batch \
    --roi 45.81 5.95 47.81 10.5 \
    --start 2022-11-19 --end 2022-11-29 \
    --satellite SENTINEL1:L2
```



# Technical specifications

## Components
### Satellites
The following satellites and respective processing levels are
included in the design:

* Sentinel-1
    * Level 1 (GRD)
    * Level 2 (GRD_SIGMA0)
* Sentinel-2
    * Level 1C
    * Level 2A
* Sentinel-3
    * Level 1B
    * Level 2
        * LFR Atmos (Land)
        * WFR Atmos (Water)

### Providers

* Copernicus Open Access Hub (SCIHUB)
    * For searching capabilities
* Alaskan Satellite Facility
    * Sentinel 1
* Sinergise
    * Sentinel 2
* NASA Common Metadata Repository
    * Sentinel 3
