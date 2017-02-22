## OOI Listings

- Research Arrays: http://oceanobservatories.org/research-arrays/
- Sites: http://oceanobservatories.org/site-list/
- Instruments: http://oceanobservatories.org/instruments/
- Data Products: http://oceanobservatories.org/data-products/data-products-complete-list/

## Table of parameters mapping for OA assets

| id  | platform_code | parameters                                                       |
|:--- |:------------- |:---------------------------------------------------------------- |
| 560 | CE09OSSM      | temperature; salinity; pH; CO2_air; *CO2_sw(1m)*; **CO2_sw(7m)** |
| 561 | GA01SUMO      | temperature; salinity; CO2_air; CO2_sw(7m); **pH**               |
| 562 | GP03FLMA      | **temperature; salinity; pH**                                    |
| 563 | CE02SHSM      | temperature; salinity; pH; CO2_air; *CO2_sw(1m)*                 |
| 564 | CE01ISSM      | temperature; salinity; pH; CO2_sw(7m)                            |
| 565 | CE04OSSM      | temperature; salinity; pH; CO2_air; *CO2_sw(1m)*                 |
| 566 | GI01SUMO      | temperature; salinity; pH; CO2_air; *CO2_sw(1m)*; CO2_sw(7m)     |
| 567 | CE06ISSM      | temperature; salinity; pH; CO2_sw(7m)                            |
| 568 | CP01CNSM      | temperature; salinity; pH; CO2_air; *CO2_sw(1m)*; CO2_sw(7m)     |
| 569 | CP03ISSM      | temperature; salinity; pH; CO2_air; *CO2_sw(1m)*; CO2_sw(7m)     |
| 570 | CP04OSSM      | temperature; salinity; pH; CO2_air; *CO2_sw(1m)*; CO2_sw(7m)     |
| 571 | CE07SHSM      | temperature; salinity; pH; CO2_air; *CO2_sw(1m)*                 |
| 572 | GS01SUMO      | temperature; salinity; pH; CO2_air; *CO2_sw(1m)*; CO2_sw(7m)     |

Notes:
- *parameter* = This parameter is part of `pCO2a` instrument which measures both CO2 in air and water.
- **parameter** = This parameter data are recovered from instrument, and are not in situ live stream.

## OOI Resource Links

- https://marine.rutgers.edu/cool/ooi/uframe-status/viz/json/uframe-instruments-all.json
- https://ooinet.oceanobservatories.org/api/asset_deployment
- https://ooinet.oceanobservatories.org/api/uframe/stream
- https://github.com/adampotocki/ref_des
- http://uframe-test.ooi.rutgers.edu:12576/sensor/inv/
- https://github.com/ooi-integration/asset-management
- https://github.com/kerfoot/ooinet-product-browser/tree/master/www/json/observatoryDataProducts
- https://github.com/asascience-open/ooi-ui-services
- https://ooinet.oceanobservatories.org/api/asset_deployment?min=True
- https://github.com/asascience-open/ooi-ui-services/blob/master/db/ooiui_schema_data.sql
- https://github.com/asascience-open
- https://marine.rutgers.edu/cool/ooi/uframe-status/
- http://ooiufs01.ooi.rutgers.edu:12576/sensor/inv/
- https://github.com/ooi-data-review/uframe-api
- https://marine.rutgers.edu/cool/ooi/uframe-status/json/status.json
- https://ooinet.oceanobservatories.org/api/array

## Raw Data Archive

Link to the structure of the Raw Data Archive can be found in the html file https://rawdata.oceanobservatories.org/files/.tree.html. **Note: It appears that this html file is not updated for each deployment, and may have some pretty old information.**

## OOI Data Vocabulary Table

| Vocab                 | Definition |
|:--------------------- |:----------- |
| BEP 	                | Benthic Experiment Package, a cabled seafloor platform containing a Low-Power Junction Box and multiple instruments inside a trawl-resistant frame |
| Cabled                | Any node or instrument attached to the electro-optical cable on the west coast |
| CPM 	                | Platform Controller (engineering data only) |
| D0000\*               | Deployment folder, aka telemetered data (sent to shore while platform is deployed) |
| DCL 	                | Data Concentrator Logger, the controller computer that concentrates the data from multiple instruments on uncabled moorings, packages the data, and telemeters to shore |
| DVL 	                | Glider ADCP, Teledyne RDI 600 kHz Explorer DVL |
| LJ0\*\*               | Low-Power Junction Box, a smaller cabled node that powers seafloor instruments, occasionally located inside a seafloor platform |
| LV0\*\*               | Low-Voltage Node, connected to the Primary Node |
| MFN 	                | A seafloor instrument frame at the base of coastal moorings, containing the anchor and acoustic release package, battery packs, and multiple instruments |
| MJ0\*\*               | Medium-Power Junction Box, a cabled node that powers seafloor instruments |
| PN0\*\*               | Primary Node, connected directly to the electro-optical cable, usually not instrumented |
| Profiler              | A mooring installation with an instrumented platform that moves up and down vertically in the water column. One type of profiler on the OOI is a wire-following modified McLane profiler (WFP) that crawls along an inductive cable using a traction motor. These are indicated by reference designator platform codes ending in “PM” for “Profiler Mooring”. The other type of profiler is a coastal surface piercing profiler (CSPP) that uses a winch to spool out line from a buoyant instrument platform, raising and lowering it in the water. This type of profiler has a platform code that ends in “SP” for “Surface Piercing”. |
| R0000\*               | Recovery folder, aka recovered data (downloaded after platform is recovered) |
| Recovered             | Data offloaded directly from an instrument or data logger; usually by connecting the instrument to a computer after the instrument has been recovered and writing to files, often onboard the recovery vessel. |
| Reference Designators | The machine-readable codes used to refer to arrays, sites, platforms, and instruments on the OOI. See reference sheet for site codes and the 5-letter instrument codes. |
| Streamed 	            | Data received via transmission over electro-optical cable. Streaming data are provided at full temporal resolution and near-real time. |
| Telemetered           | Data received through a transmission media over distance. Examples are: surface buoy to satellite, glider to satellite, acoustic modem. Data received through satellite relay or other mechanisms results in “batch” receipt and may be decimated in time. These data have greater latencies than the streaming data. |
| Uncabled 	            | Any platform (mooring, glider, or profiler) not attached to the electro-optical cable on the west coast |
| X0000\* 	            | Test data, collected on deck or during integration and burn-in testing. Use at your own risk. |


## Email Exchanges

Subject: OOI network-wide platform metadata?
  - Date: 9/8/2016
    - Calibration sheets can be found at https://github.com/ooi-integration/asset-management/tree/master/deployment
    - To parse calibration sheets, a script can be found at https://github.com/ooi-data-review/parse_cal_sheets/blob/master/parse_cal_sheets.py

Subject: OOI data harvesting: working on new instruments (Chl a, pH, pCO2)?
  - Date: 8/10/2016
    - the PCO2A sensor makes two measurements (in-air and in-water PCO2). Because this sensor produces PCO2 water observations at about 1 m depth, the coastal surface moorings (CE02, 04, 07 and 09) do not have PCO2W measurements at 7 meters. The inshore moorings on the other hand do have PCO2W measurements at 7 meters.
  - Date: 8/9/2016
    - The phsen2 and pco2w2 sensors on the CE01ISSM MFN are missing. These data will be associated with DCL16. I think the reason they are not there now is that right before the mooring was deployed in the spring the DCL died and so the MFN was deployed with internally recording sensors, i.e. we are not getting NRT data from the MFN sensors. Hopefully when CE01ISSM is deployed next month we will have PHSEN and PCO2W data for the MFN. These data will be collected at a depth of 25m.
  - Date 8/2/2016
    - Link to updated parser: https://github.com/cwingard/cgsn-parsers/tree/pypi
    - For the instruments you are after:
      - Chlorophyll a -- FLORT on the NSIF (DCL16 for CE0[16]ISSM and DCL27 for CE0[2479]*SM. This instrument is the WET Labs ECO Triplet. Data is in raw counts. We will need to work on getting you calibration coefficients.
      - pH -- PHSEN on the NSIF (as above, except DCL26 for CE0[2479]*SM). This is the Sunburst Sensors SAMI2-pH reporting the data as ASCIIHEX strings. I do have code used to process the data to calculate pH.
      - pCO2 in water -- PCO2A (on CE0[2479]*SM) and PCO2W (on DCL16 of CE0[16]ISSM) both provide a measurement of pCO2 in water (at 1 m depth and 7 m depth, respectively). The PCO2A (from Pro-Oceanus) data is the most readily available for integration. The PCO2W (from Sunburst Sensors, SAMI2-pCO2) will require further work.
      - pCO2 in air -- PCO2A (on CE0[2479]*SM) measures the pCO2 in air with intake located slightly less than 2 meters above the surface.
      - turbidity -- FLORT on the NSIF (as above) measures optical backscatter at 700 nm with the calibration converting the raw counts to m^-1 sr^1. Code does exist to convert this data to particulate backscatter (bb, m^-1).


