# Esri UK Annual Conference 2026

This folder contains code from the **2026 Esri UK Annual Conference**. The two sub-folders each correspond to one of the two ArcPy demos presented at the conference.

## Overview

This session explores automating site suitability analysis with Python across ArcGIS Pro and ArcGIS Online.  
 
In ArcGIS Pro, we show how to convert a multi-step site suitability workflow into a single Python tool with minimal hands-on coding required, and how to share it with colleagues who can add it to their own workflows.  
 
The ArcGIS Online demo accesses this script as a Python module inside an ArcGIS Notebook. It uses it to solve a real suitability problem - ranking candidate locations by how closely they match the catchment profile of existing businesses - all from a browser! 

## Demos

### ArcGIS Pro

Code demonstrating how to work with ArcPy inside ArcGIS Pro, using the Network Analyst extension to generate a catchment (service area) around a point of interest and summarise census data within it.

| File                                                                                                              | Description                                                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`modelBuilderPythonScript.py`](ArcGIS%20Pro/modelBuilderPythonScript.py)                                         | Auto-generated Python script exported directly from an ArcGIS Pro ModelBuilder model. Produces a 15-minute walking isochrone around a standing location and summarises census data within the resulting polygon.                                                |
| [`ArcGIS_Location_Service_Catchment_Generation.py`](ArcGIS%20Pro/ArcGIS_Location_Service_Catchment_generation.py) | A modified and extended version of the ModelBuilder script, refactored to include robust error handling, progress messaging via `arcpy.AddMessage`, dynamic output path derivation, and a cleaner code structure suitable for use as an ArcGIS Pro Script Tool. |

#### What the script does

`ArcGIS_Location_Service_Catchment_generation.py` is an ArcGIS Pro Script Tool that runs in nine steps:

1. **Read tool parameters** — accepts three inputs: a feature set of starting points, a travel time cutoff in minutes, and a census summary feature layer.

2. **Derive output paths** — constructs output paths dynamically from the current ArcGIS Pro project's default geodatabase and the name of the input layer, so no hardcoded paths are needed.

3. **Connect to ArcGIS Location Services** — uses `arcpy.nax.GetTravelModes()` against `https://www.arcgis.com` to retrieve available travel modes, authenticated via the active ArcGIS Online sign-in in ArcGIS Pro.

4. **Configure the Service Area solver** — sets up `arcpy.nax.ServiceArea` with the Walking Time travel mode, the supplied cutoff, high-detail filled polygon geometry (`Disks`), and no time-of-day dependency (pedestrian routing is time-independent).

5. **Load facilities** — loads the input starting points into the solver as facilities.

6. **Solve** — executes the service area solve against ArcGIS Location Services. Solver messages are surfaced via `arcpy.AddMessage` and `arcpy.AddError`; the tool exits cleanly if the solve fails.

7. **Export the isochrone** — writes the output polygon(s) to the derived geodatabase path.

8. **Summarise census data** — runs `arcpy.analysis.SummarizeWithin` to intersect the isochrone with the supplied census feature layer, producing a summary table of the demographic data within the catchment.

9. **Add to the active map** — attempts to add the census summary output to the currently active ArcGIS Pro map, with a warning if no map is open.

#### Using this script in your own workflows

- **As a Script Tool** — attach the script to a Script Tool in an ArcGIS Pro toolbox. The three parameters (starting points, travel time, census layer) are defined in the tool properties and passed to the script via `arcpy.GetParameter`.
- **Different travel time** — the cutoff is fully parameterised; pass any integer (e.g. `10` or `20`) to generate a different isochrone without touching the code.
- **Different census data** — swap the census feature layer parameter for any polygon or point feature class to summarise different demographic or land-use data within the catchment.
- **Connection to the ArcGIS Online notebook** — this script is the ArcGIS Pro counterpart to the walking catchment logic used in the ArcGIS Online notebook. The core approach — calling ArcGIS Location Services to generate a walking isochrone, then intersecting it with a census dataset — is the same in both environments. The Python module (`Catchment_profile_tool.py`) used in the notebook was developed from this script: it is uploaded to ArcGIS Online as a notebook file and ingested by the notebook at runtime, carrying the same routing and Census querying logic into the cloud environment so that the two demos share a common analytical foundation.

### ArcGIS Online

Code demonstrating how to combine the ArcGIS API for Python, `arcpy`, and open-source Python tools inside an **ArcGIS Notebook** to perform location suitability analysis entirely in the browser — no desktop software and no data downloads required.

The scenario: Ahmad and Ben decide to open a bakery and need to figure out which of three candidate locations sits in a neighbourhood that most closely resembles the areas where existing bakeries already succeed.

| File                                                                                                    | Description                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Where's_the_best_place_for_our_bakery.ipynb`](ArcGIS%20Online/b03bd5244db64ee7a89e724c474b13dd.ipynb) | End-to-end suitability notebook. Queries Overture Maps on Amazon S3 for existing bakeries, generates 15-minute walking catchments via the ArcGIS routing service, profiles each catchment using Census 2021 occupation data, scores three candidate locations against the benchmark, visualises the results, and publishes the output back to ArcGIS Online as hosted feature layers. |

#### What the notebook does

The analysis runs in seven steps:

1. **Imports & sign-in** — authenticates to ArcGIS Online (`GIS('home')`) and loads the required libraries: `arcpy`, the ArcGIS API for Python, `duckdb`, `pandas`, and `matplotlib`, plus a custom `Catchment_profile_tool` module that encapsulates the walking area generation and Census querying logic.

2. **Configuration** — all parameters (`CANDIDATES_ITEM_ID`, `BBOX`, `PLACE_CATEGORY`) are declared in a single cell. These are also exposed as tool parameters so the notebook can be published as a custom ArcGIS tool and driven through a form interface. Changing the bounding box and place category is all that is needed to re-run the analysis for a different city or business type.

3. **Build the benchmark** — [DuckDB](https://duckdb.org/) queries the [Overture Maps](https://overturemaps.org/) places dataset directly from Amazon S3 using SQL, returning only the matching rows for the chosen place category within the bounding box. The resulting points are passed to the custom module, which calls the ArcGIS Online routing service to generate a 15-minute walking polygon around each location and then queries the ONS Census 2021 TS063 occupation dataset (hosted as a public FeatureServer by Esri UK) to build a median occupation profile across all the Output Areas that fall within those catchments. This combined profile becomes the **benchmark** — a description of the kind of neighbourhood where the chosen business type tends to operate.

4. **Profile the candidates** — the same walking catchment and Census querying process is repeated for each of the three candidate locations, which are stored as a hosted feature layer on ArcGIS Online. Each candidate receives its own individual occupation profile.

5. **Score and rank** — each candidate is assigned a **gap score**: the sum of the absolute percentage-point differences between its occupation profile and the benchmark across all nine Standard Occupational Classification groups. A lower score means a closer match to where existing bakeries succeed.

6. **Visualise** — a `matplotlib` deviation chart plots each candidate's profile relative to the benchmark (dashed line at zero), with a shaded band indicating a ±5 percentage-point tolerance. The chart shows not just which candidate wins but which specific occupation groups make it a better or worse fit.

7. **Publish** — the walking area polygons and the scored candidate points are written back to ArcGIS Online as new hosted feature layers using `spatial.to_featurelayer()`.

#### Using this notebook in your own workflows

The notebook is designed to be modular and reusable:

- **Different place type or city** — edit `PLACE_CATEGORY` and `BBOX` in the configuration cell and re-run. No other changes are needed.
- **Different demographic benchmark** — the Census FeatureServer URL and field mapping (`OCC_URL`, `OCC_FIELDS`) are declared in the configuration section. Swap these for any other publicly accessible ONS or Esri UK demographic FeatureServer to benchmark against a different Census variable.
- **Different travel mode or walk time** — adjust `SA_BREAK_VALUES`, `SA_BREAK_UNITS`, and `SA_TRAVEL_MODE` in the configuration section to switch between walking, driving, or cycling isochrones.
- **Custom module** — the `Catchment_profile_tool.py` module that handles routing and Census querying is kept separate from the notebook. It can be reused in other notebooks to add catchment profiling to any point-based analysis.
- **Published as a custom tool** — because the three key parameters are tagged for tool exposure, the notebook can be published to ArcGIS Online as a custom geoprocessing tool, allowing other users to run the analysis through a form without seeing or editing the code.
