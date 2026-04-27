# Esri UK Annual Conference 2026

This folder contains code from the **2026 Esri UK Annual Conference**. The two sub-folders each correspond to one of the two ArcPy demos presented at the conference.

## Demos

### ArcGIS Pro

Code demonstrating how to work with ArcPy inside ArcGIS Pro, using the Network Analyst extension to generate a catchment (service area) around a point of interest and summarise census data within it.

| File                                                                                                              | Description                                                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`modelBuilderPythonScript.py`](ArcGIS%20Pro/modelBuilderPythonScript.py)                                         | Auto-generated Python script exported directly from an ArcGIS Pro ModelBuilder model. Produces a 15-minute walking isochrone around a standing location and summarises census data within the resulting polygon.                                                |
| [`ArcGIS_Location_Service_Catchment_generation.py`](ArcGIS%20Pro/ArcGIS_Location_Service_Catchment_generation.py) | A modified and extended version of the ModelBuilder script, refactored to include robust error handling, progress messaging via `arcpy.AddMessage`, dynamic output path derivation, and a cleaner code structure suitable for use as an ArcGIS Pro Script Tool. |

### ArcGIS Online

> Content for this demo will be added here.
