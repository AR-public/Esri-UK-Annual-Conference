# ---------------------------------------------------------------------------
# ArcGIS_Location_Service_Catchment_generation.py
#
# ArcGIS Pro Script Tool
# Generates a 15-minute walking isochrone (service area) for one or more
# starting points using Esri's ArcGIS Location Services.
#
# Tool Parameters (defined in the the Script Tool properties in ArcGIS Pro):
#   0 – Input Starting Points  | Feature Set    | Required | Input
#   1 – Travel Time (minutes)  | Long           | Required | Input
#   2 – Census Summary Data    | Feature Layer  | Required | Input
#
# NOTE: Requires an active ArcGIS Online / Portal sign-in in ArcGIS Pro.
#       Solving the service area consumes ArcGIS Online credits.
# ---------------------------------------------------------------------------

import arcpy # type: ignore
import os


def main():

    # ------------------------------------------------------------------
    # 1.  Read tool parameters
    # ------------------------------------------------------------------
    point_of_interest  = arcpy.GetParameter(0)       # Feature Set or Feature Layer
    travel_time       = arcpy.GetParameter(1)       # Travel time cutoff in minutes (integer)
    census_data       = arcpy.GetParameterAsText(2) # Census summary Feature Layer

    # ------------------------------------------------------------------
    # 2.  Derive output paths from the input layer name + project default GDB
    # ------------------------------------------------------------------
    aprx        = arcpy.mp.ArcGISProject("CURRENT")
    default_gdb = aprx.defaultGeodatabase

    input_raw  = arcpy.GetParameterAsText(0)
    input_base = arcpy.ValidateTableName(
        os.path.splitext(os.path.basename(input_raw))[0] if input_raw else "StartingPoints"
    )
    output_polygons = os.path.join(default_gdb, input_base + "_ServiceArea")
    output_summary  = os.path.join(default_gdb, input_base + "_CensusSummary")

    arcpy.AddMessage(f"Output isochrone  : {output_polygons}")
    arcpy.AddMessage(f"Output census summary: {output_summary}")

    # ------------------------------------------------------------------
    # 3.  Network data source – ArcGIS Location Services via ArcGIS Online
    #     The active portal sign-in in ArcGIS Pro provides authentication.
    # ------------------------------------------------------------------
    network_data_source = "https://www.arcgis.com"

    arcpy.AddMessage("Retrieving travel modes from ArcGIS Location Services...")
    try:
        travel_modes = arcpy.nax.GetTravelModes(network_data_source)
    except Exception as e:
        arcpy.AddError(
            "Could not retrieve travel modes from ArcGIS Location Services. "
            "Ensure you are signed in to ArcGIS Online (or your portal) in ArcGIS Pro.\n"
            f"Details: {e}"
        )
        return

    # Walking Time is the standard pedestrian travel mode on ArcGIS Online
    travel_mode_name = "Walking Time"
    if travel_mode_name not in travel_modes:
        arcpy.AddError(
            f"Travel mode '{travel_mode_name}' was not found on the network data source. "
            f"Available modes: {list(travel_modes.keys())}"
        )
        return

    # ------------------------------------------------------------------
    # 4.  Configure the Service Area solver
    # ------------------------------------------------------------------
    arcpy.AddMessage(f"Configuring {travel_time}-minute walking service area solver...")

    sa = arcpy.nax.ServiceArea(network_data_source)

    # Travel mode and cutoff
    sa.travelMode              = travel_modes[travel_mode_name]
    sa.defaultImpedanceCutoffs = [travel_time]

    # Geometry options – Disks produces a filled isochrone polygon
    sa.geometryAtCutoff  = arcpy.nax.ServiceAreaPolygonCutoffGeometry.Disks
    sa.polygonDetail     = arcpy.nax.ServiceAreaPolygonDetail.High

    # Walking is not time-of-day dependent, so leave as None
    sa.timeOfDay = None

    # ------------------------------------------------------------------
    # 5.  Load starting points as facilities
    # ------------------------------------------------------------------
    arcpy.AddMessage("Loading starting point(s)...")
    sa.load(arcpy.nax.ServiceAreaInputDataType.Facilities, point_of_interest)

    # ------------------------------------------------------------------
    # 6.  Solve
    # ------------------------------------------------------------------
    arcpy.AddMessage(
        "Solving service area using ArcGIS Location Services "
        "(this operation consumes ArcGIS Online credits)..."
    )
    result = sa.solve()

    if not result.solveSucceeded:
        arcpy.AddError("Service area solve failed. See messages below:")
        for msg in result.solverMessages(arcpy.nax.MessageSeverity.All):
            arcpy.AddError(msg[-1])
        return

    # Log any informational messages returned by the solver
    for msg in result.solverMessages(arcpy.nax.MessageSeverity.All):
        arcpy.AddMessage(msg[-1])

    # ------------------------------------------------------------------
    # 7.  Export the output isochrone polygon(s)
    # ------------------------------------------------------------------
    arcpy.AddMessage("Exporting isochrone polygon(s)...")
    result.export(arcpy.nax.ServiceAreaOutputDataType.Polygons, output_polygons)

    arcpy.AddMessage(f"15-minute walking isochrone saved to: {output_polygons}")

    # --------------------------------------------------------------------------------
    # 8.  Summarise census data within the isochrone polygon using SummarizeWithin
    # --------------------------------------------------------------------------------
    arcpy.AddMessage("Summarizing census data within service area...")

    # Process: Summarize Within (SummarizeWithin) (analysis)
    arcpy.AddMessage(f"Running Summarize Within against '{output_polygons}'...")
    arcpy.analysis.SummarizeWithin(in_polygons=output_polygons, in_sum_features=census_data, out_feature_class=output_summary, keep_all_polygons="KEEP_ALL", sum_fields=[["B19049_001E", "Mean"], ["B19053_001E", "Mean"]], sum_shape="ADD_SHAPE_SUM", shape_unit="SQUAREMILES")
    arcpy.AddMessage(f"Summarize Within complete. Output: {output_summary}")

    arcpy.AddMessage(f"Census summary saved to: {output_summary}")

    # ------------------------------------------------------------------
    # 9.  Add the census summary layer to the active map
    # ------------------------------------------------------------------
    arcpy.AddMessage("Adding census summary layer to the map...")
    try:
        active_map = aprx.activeMap
        if active_map is None:
            arcpy.AddWarning(
                "No active map found – census summary layer was not added to the map. "
                "Open a map and re-run, or add the layer manually."
            )
        else:
            active_map.addDataFromPath(output_summary)
            arcpy.AddMessage("Census summary layer added to the map.")
    except Exception as e:
        arcpy.AddWarning(f"Could not add census summary layer to the map: {e}")


if __name__ == "__main__":
    main()
