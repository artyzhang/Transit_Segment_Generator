import arcpy
import pandas as pd

# Open the node to node spreadsheet
def_table = r'G:\01_Projects\TransitServicePlanning\CorridorSpeedAnalysis\02_OtherData\Working\Stop to Stop Route Segments.xlsx'
def_tabledf = pd.read_excel(def_table)

# Open the trc_df spreadsheet
trc_2019 = r'G:\01_Projects\TransitServicePlanning\CorridorSpeedAnalysis\02_OtherData\Working\Scripting\trc_join_2019.csv'
trc_df = pd.read_csv(trc_2019)

def createrangetuples(inlist):
    # Pairs items in a list with its following value to return a list of tuples
    return [(inlist[a],inlist[a+1]) for a in range(len(inlist)-1)]

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

# Begin reading the pattern specification table
# Format the routes and directions into a concatenated pattern
routeanddirectionlist = []
for item in zip(def_tabledf['Route'], def_tabledf['Direction']):
    a = str(item[0]).ljust(5, " ")
    if item[1] == 'INBOUND':
        b = 'I'
    elif item[1] == 'OUTBOUND':
        b = 'O'
    routeanddirectionlist.append(a+b)
# Put the pattern as a column in the definition dataframe
def_tabledf['PATTERN_SPEC'] = pd.Series(routeanddirectionlist)

# Create a dictionary for the node to node list
spec_list = def_tabledf.loc[:,'PATTERN_SPEC'].unique()
spec_dict = {}
for item in spec_list:
    filter_defdf0 = def_tabledf[def_tabledf['PATTERN_SPEC'] == item]
    nodetonodetuples = zip(filter_defdf0['FromStopID'], filter_defdf0['ToStopID'])
    seg_name = [s for s in filter_defdf0['SegmentName']]
    nodetonodelist = []
    for fromto in nodetonodetuples:
        if fromto[0] not in nodetonodelist: 
            nodetonodelist.append(fromto[0])
        if fromto[1] not in nodetonodelist: 
            nodetonodelist.append(fromto[1])
    spec_dict[item] = [seg_name, nodetonodelist, nodetonodetuples]

# Begin reading the Trace Dataset
# Isolate the full patterns from trc_df
potentialkeys = [n for n in trc_df['PatternName'].unique()]
fullkeys = {}
for item in potentialkeys:
    if str(item)[:6] in spec_list:
        if str(item)[-3] == 'F':
            fullkeys[item] = []

# Clean up the trace data. Divides X and Y by 1000000
trc_df['XY'] = trc_df.loc[:,['X','Y']].apply(lambda row: (row['X']/1000000.000000, row['Y']/1000000.000000), axis =1)

# Assemble the row for each pattern and assign it to a dictionary
missingjoinvalues = {}
for item in fullkeys.keys():
    # pattern
    patt_spec = item[:6]
    # route
    routev = item[:4].strip(' ')
    # direction
    directionv = item[5]
    # segment name
    segment_name = spec_dict[patt_spec][0]
    # Node to node list
    patternspeclist = spec_dict[patt_spec][1]
    # List of nodes and XY coordinates to make the final nodes and points layer
    filter_df = trc_df[trc_df['PatternName'] == item].sort_values('Sequence')
    pointslist = zip(filter_df['PointID'],filter_df['XY'])
    nodesandpoints = splitzippedlistbyanother(pointslist,patternspeclist)
    # List starting and ending nodes for each of the features
    nodestonodes = []
    for k in nodesandpoints[0]:
        nodestonodes.append((k[0][0],k[-1][0]))
    # Create the spatial data list for each pattern: route, direction, a list of node to node tuples, then a list of tuples for each XY for each node to node.
    fullkeys[item] = [routev, directionv, segment_name, patternspeclist, nodestonodes, nodesandpoints[0]]
    # Put the missing values in a different dictionary
    missingjoinvalues[item] = nodesandpoints[1]
 
# Create the new feature class
geodb = r'G:\01_Projects\TransitServicePlanning\CorridorSpeedAnalysis\01_Geodata\Working\TransitSegment_Generation.gdb'
fin_transitseg = arcpy.CreateFeatureclass_management(geodb,"transitsegs_test03","POLYLINE",spatial_reference = 4269)
fin_transitseg = r'G:\01_Projects\TransitServicePlanning\CorridorSpeedAnalysis\01_Geodata\Working\TransitSegment_Generation.gdb\transitsegs_test03'
arcpy.AddField_management(fin_transitseg,'PATTERN','TEXT')
arcpy.AddField_management(fin_transitseg,'ROUTE_NAME','TEXT')
arcpy.AddField_management(fin_transitseg,'DIRECTION','TEXT')
arcpy.AddField_management(fin_transitseg,'SEGMENTNAME','TEXT')
arcpy.AddField_management(fin_transitseg,'ORIG_NODES','TEXT')
arcpy.AddField_management(fin_transitseg,'FROM_NODE','FLOAT')
arcpy.AddField_management(fin_transitseg,'TO_NODE','FLOAT')

with arcpy.da.InsertCursor(fin_transitseg,['PATTERN','ROUTE_NAME','DIRECTION', 'SEGMENTNAME','ORIG_NODES','FROM_NODE','TO_NODE','SHAPE@']) as cur:
    for pattern in fullkeys.keys():
        for segmentnum in range(len(fullkeys[pattern][5])):
            row1 = [pattern, # Pattern
                fullkeys[pattern][0], # Route Name
                fullkeys[pattern][1], # Direction
                fullkeys[pattern][2][segmentnum], # Segment Name
                str(fullkeys[pattern][3]), # Original from and to nodes
                fullkeys[pattern][4][segmentnum][0], # from node
                fullkeys[pattern][4][segmentnum][1]] # to node 
            finxylist = [y for (x,y) in fullkeys[pattern][5][segmentnum] if y != (0,0)]
            points = []
            for x in finxylist:
                points.append(arcpy.Point(*coords) for coords in finxylist)
            line = arcpy.Polyline(arcpy.Array(points))
            row1.append(line)
            cur.insertRow(row1)