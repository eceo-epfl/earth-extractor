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

# Getting started
## Installation

### Install from git

If poetry is not installed locally, install it first with:

```bash
pip install poetry
```

Then install the package with:

```bash
git clone https://github.com/eceo-epfl/earth-extractor
cd earth-extractor
poetry install
```

## Example usage (CLI)

Search for Sentinel-1 L2A data for Switzerland between the dates
2022-11-19 and 2022-11-29.

```bash
earth_extractor/app.py \
    --roi 45.81 5.95 47.81 10.5 \
    --start 2022-11-19 --end 2022-11-29 \
    --satellite SENTINEL2:L2A
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
