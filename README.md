# earth-extractor
A library to simplify the workflow of data acquisition from multiple
satellite data providers

This library intends to simplify the data acquisition process for a select
amount of satellite providers and is deliberately written to provide a
hands-off approach for simple data collection. This is dissimilar to projects
such as EODag and getSpatialData which aim to harmonise the process over many
providers and satellite types.

### Satellites
At this stage the following satellites and respective processing levels are
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
* Singergise
    * Sentinel 2
* NASA Common Metadata Repository
    * Sentinel 3
