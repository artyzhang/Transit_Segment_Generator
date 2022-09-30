# Create bus route layer

# Create stops layer

# Choose a route 

''' OPTION 1 '''

# Create new feature class

# Create a copy of the route in new feature class

# Return list of stops that serve the route 

# Snap all stops along the route to the route

# Split line by points 

# Dissolve the line again

# Retrieve list of XY for the route

''' OPTION 2 '''

# Create new feature class

# Create a copy of the route in new feature class

# Return list of stops that serve the route 

# Retrieve lat longs for the whole route

# For each stop:
# Check if the stop is in the lat long list. If yes, move on

# If not, find the closest lat long in the list, get the index
# Find the second closest lat long in the list, get the index
# Make a point object 
# Then insert the lat long between those lat longs

# Go back to the beginning of the route XY list
# For each stop to stop pair run compare return index and splitzippedlistbyanother (rewrite code so it uses enumerate instead)

def comparereturnindex(l1,l2):
    # Returns the index of where items in a second list appear in the first list, along with missing values
    splitvalues = []
    missingvalues = []
    for item in l2:
        if item in l1:
            splitvalues.append(l1.index(item))
        else:
            missingvalues.append(item)
    return [splitvalues,missingvalues]

def splitzippedlistbyanother(zippedlist, splitvalues, inclusive=True):
    # Split half of a zipped list by the designated break points in a second list. If all items in the first list should be preserved, inclusive is True.
    sliceindex = comparereturnindex([x for (x,y) in zippedlist],splitvalues)[0]
    missingindex = comparereturnindex([x for (x,y) in zippedlist],splitvalues)[1]
    if len(sliceindex) == 1:
        singlevalue = sliceindex[0]
        sliceindex = [0,singlevalue,len(zippedlist)-1]
    if inclusive == True:
        sliceindex[0] = 0
        sliceindex[-1] = len(zippedlist)-1
    sliceranges = createrangetuples(sliceindex)
    listoflists = []
    for r in sliceranges:
        listoflists.append(zippedlist[r[0]:r[1]+1])
    return [listoflists,missingindex]

# Create a row for each segment with route ID, direction, etc.
# Create a from node and to node
# Put in stop IDs in from and to 
# Add polyline object to the row

# Put row in the feature class using InsertCursor

from math import cos, asin, sqrt

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    hav = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(hav))

def closest(data, v):
    return min(data, key=lambda p: distance(v['lat'],v['lon'],p['lat'],p['lon']))


'''
    def _make_line_from_shape(self, shape_id):
        """Make a polyline object by connecting the lat/lon points for a given shape_id.

        Args:
            shape_id: GTFS shape_id to pull from the table and convert to a polyline
        Returns:
            arcpy polyline object for this shape_id
        Raises:
            No exceptions.
        """
        # Fetch the shape points for this shape_id, in order.
        this_shape_df = self.shapes_table.data_frame.get_group(shape_id).sort_values(by="shape_pt_sequence")

        # Create the polyline feature from the sequence of points
        lats = this_shape_df[self.shapes_table.lat_field].tolist()
        lons = this_shape_df[self.shapes_table.lon_field].tolist()
        array = arcpy.Array()
        for idx, lat in enumerate(lats):
            point = arcpy.Point()
            point.X = float(lons[idx])
            point.Y = float(lat)
            array.add(point)
        polyline = arcpy.Polyline(array, gtfs_utils.WGS_COORDS)

        return polyline
'''
