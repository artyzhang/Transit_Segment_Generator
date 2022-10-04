# Tool that cuts a line by a list of points

# Run near tool
arcpy.analysis.Near('bk_pattern_stops','bk_bus_shapes',location='LOCATION')

def linevertices(polyline): # Return point data for a polyline
    return [(point.X,point.Y) for point in polyline[0]]

def getxydata(fc, fc_field, valuelist): # Return lat longs for a point or a polyline
    if arcpy.Describe(fc).shapeType == 'Polyline':
        with arcpy.da.SearchCursor(fc, [fc_field,'SHAPE@']) as cursor:
            xys = []
            for row in cursor:
                if row[0] in valuelist:
                    xys.append(row[1])
            return [linevertices(line) for line in xys]
    elif arcpy.Describe(fc).shapeType == 'Point':
        with arcpy.da.SearchCursor(fc, [fc_field,'SHAPE@XY']) as cursor:
            xys = []
            for row in cursor:
                if row[0] in valuelist:
                    xys.append(row[1])
            return xys

def getnearxy(fc): # Return near x and near y coordinates
    with arcpy.da.SearchCursor(fc, ['NEAR_X','NEAR_Y']) as cursor:
        xys = []
        for row in cursor:
            xys.append((row[0],row[1]))
        return xys
                           
newnear = getnearxy('bk_pattern_stops')

def arcpt(coord): # Create Point Geometry from lat long tuple
    sr = arcpy.SpatialReference(4326)
    return arcpy.PointGeometry(arcpy.Point(*coord),sr)

def findtwoclosest(in_point, points_list): # Finds where in the line to insert a lat long point 
    start = arcpt(in_point)
    distances = [start.distanceTo(arcpt(point2)) for point2 in points_list]
    ordered = sorted(distances)
    begin = distances.index(ordered[0])
    end = distances.index(ordered[1])
    return (begin, end)

def closest(in_point,points_list): # For a given lat long, finds the closest point from a list of points
    start = arcpt(in_point)
    distances = [start.distanceTo(arcpt(point2)) for point2 in points_list]
    return distances.index(min(distances))

def insertpointsintoline(in_points,points_list): # Insert points into line
    newline = points_list
    for newpoint in in_points:
        between = findtwoclosest(newpoint,newline) 
        if between[0] <= between[1]:
            insertat = between[0]
        else:
            insertat = between[1]
        newline.insert(insertat,newpoint)
    return newline
    
def createsubstring(from_point,to_point,points_list, startof=False, endof=False):
    if startof == True:
        start = 0
    else:
        start = points_list.index(from_point)
    if endof == True:
        end = -1
    else:
        end = points_list.index(to_point) + 1
    return points_list[start:end]

def constructsubstring(stop_points, line_points):
    linewithpoints = insertpointsintoline(stop_points,line_points)
    newline = []
    for i, stop in enumerate(stop_points):
        if i < len(stop_points) - 1:
            to_stop = stop_points[i+1]
            if i == 0:
                newline.append(createsubstring(stop, to_stop, linewithpoints, startof=True))
            elif i == len(stop_points)-1:
                newline.append(createsubstring(stop, to_stop, linewithpoints, endof=True))
            else:
                newline.append(createsubstring(stop, to_stop, linewithpoints))
    return newline

newline = constructsubstring(newnear,routexys[0])

# Create a row for each segment with route ID, direction, etc.
# Create a from node and to node
# Put in stop IDs in from and to 
# Add polyline object to the row

# Put row in the feature class using InsertCursor

geodb = r'C:\Users\1280530\GIS\GTFS to Feature Class\Points_Near.gdb'
arcpy.CreateFeatureclass_management(geodb,"transitseg_test","POLYLINE",spatial_reference = 4326)

with arcpy.da.InsertCursor("transitseg_test",['SHAPE@']) as cur:
    sr = arcpy.SpatialReference(4326)
    for segment in newline:
        array = arcpy.Array()
        for x,y in segment:
            point = arcpy.Point()
            point.X = float(x)
            point.Y = float(y)
            array.add(point)
        polyline = arcpy.Polyline(array,sr)
        cur.insertRow([polyline])
