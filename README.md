# Transit_Segment_Generator
This tool takes in GTFS data, joins the trace data (trc.csv) and point-to-point data (ptp.csv), and generates an ArcGIS feature class containing all transit routes. Each transit route is split up into stop-to-stop segments. 
The resulting stop-to-stop segment data can be useful for measuring distance between stops or for joining segment-specific route data. For example, stop-to-stop segment data could be joined with speed data to show average speed during different parts of the route, ridership data to visualize loads, or customer survey data to show demographics along the route. 
Major bugs: currently, the constructed segments are missing the last lat-long point.
