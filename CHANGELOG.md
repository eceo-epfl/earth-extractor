# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2023-08-24
### Added
- Add an `--overwrite` flag to the CLI to overwrite existing files
- On downloads using the internal download function, if the file size differs,
the file is redownloaded. This is to prevent incomplete downloads.
- Metadata to the geojson export file giving the parameters of the search
query

### Fixed
- PIPE output fixed, it was giving a list of the search result objects rather
than the entire GeoJSON and contains debug msg.
- GeoJSON output merged together, if there was more than one satellite it
would be a list of geojsons, now they are just one
- Isolate the tests from the local keyring by adding the environment variable
in the pytest properties to use a different keyring.

### Changed
- Disable hide prompt in secret generation. Reason: The hidden prompt reduces
ability to understand if they are typed in correctly and credentials aren't
very confidential.
- The geojson filename is a shorter timestamp and includes the satellites.

## [0.1.0] - 2023-08-02
### Added
- MODIS and VIIRS satellites by querying and downloading from the NASA
Earthdata STAC service
- SwissImage data from SwissTopo
- Unit tests for NASA querying
- Parallelised download common functions in `earth_extractor.core.utils`
- Progress bar for downloads using the requests library (NASA STAC, SwissTopo)

### Fixed
- Setting of fake credentials for testing

### Changed
- Type hinting for python 3.8 compatibility by using fixtures in typing module
- Added `black` for code formatting

## [0.0.2] - 2023-07-17

### Fixed
- Filters on cloud_cover were affecting satellites that cannot be filtered this way. At this stage, only Sentinel 1 is affected as it is radar. What was happening was there were no records returning when a cloud_cover range was given. Filters were added to the satellites -- In this case, only `CLOUD_COVER` is needed right now, and logic was provided to ignore the filter if the search is done on this specific satellite
- Logs were not following the output folder, now they do
- Sentinel 3 has two products for Level 2, only one was provided, this meant that adding more meant this should be a list, so work was done to consider iterating through this list

### Added

- The search query can be outputted, by default it's disabled but it can run with the `--export [PIPE|FILE]` CLI option. The PIPE will output to stdout and the file option will save a GeoJSON. This file's records can be edited for example in a text editor or GIS to remove records that aren't required. Then the contents may be downloaded by using the import-geojson command.
- A query can now find the best filter (cloud cover at this stage) for a given frequency. ie. For a search over four months, and a frequency filter of monthly, will provide four records with the lowest cloud-cover range.
- Tests have been written for some methods and removed those that access outside APIs. Those that test API level requests have been mocked.
- A more robust retry method (using tenacity) is used in the case that the SentinelHubAPI has too many requests.

### Changed
- A common search result model (models.CommonSearchResult)is now used to cast the results from any provider into another providers output. The function translate_query_results is used to parse the provider's result to this model, and download methods have also been altered to define their search/download strategies from this model.

## [0.0.1] - 2023-07-05

### Added

- First revision of library with first working example with Copernicus Open
Access Hub and Alaskan Satellite Facility to download Sentinel-1, 2 and 3 data.
