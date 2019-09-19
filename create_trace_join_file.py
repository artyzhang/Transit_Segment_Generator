# Generates a joined excel sheet from the trc, ptp, and ArcGIS stops points.

import pandas as pd
import arcpy

trc_source = r'G:\01_Projects\TransitServicePlanning\CorridorSpeedAnalysis\02_OtherData\Working\stoppoints_nextbus\trc_2019.csv'
ptp_source = r'G:\01_Projects\TransitServicePlanning\CorridorSpeedAnalysis\02_OtherData\Working\stoppoints_nextbus\ptp_2019.csv'
sds_stops = r'C:\Users\AZhang3\AppData\Roaming\ESRI\Desktop10.5\ArcCatalog\MTA Spatial Data Store.sde\MTA.Transit\MTA.Muni_stops'

trc = pd.read_csv(trc_source, header = None)
ptp = pd.read_csv(ptp_source, header = None)

# Define column names. This information is taken from the Trapeze Standard Data Exchange document (v12.0 as of 9/18/2019)
trc_columns = {0: 'TraceID',
1: 'PointID',
2: 'PointType',
3: 'Sequence',
4: 'Longitude',
5: 'Latitude',
}
trc.rename(columns = trc_columns,inplace = True)

ptp_columns = {0: 'VersionID',
1: 'LineID',
2: 'DirectionID',
3: 'PatternID',
4: 'SeqNumber',
5: 'PatternName',
6: 'PatternDestination',
7: 'PointID',
8: 'PointType',
9: 'Distance',
10: 'NodeDistance',
11: 'StopDistance',
12: 'CommentID',
13: 'StopFlag',
14: 'TraceID',
15: 'LinePointSeqNum',
}
ptp.rename(columns = ptp_columns,inplace = True)

stops_latlong_dict = {}
with arcpy.da.SearchCursor(sds_stops, ['STOPID','LONGITUDE','LATITUDE','STOPNAME']) as cursor1:
    for row in cursor1:
        stops_latlong_dict[row[0]] = [row[1]*1000000,row[2]*1000000,row[3]]

def getmissingxyvalues(row, pickxy):
    # Finds blank X or Y values in the stops dictionary from Spatial Data Store
    stopid = row['PointID']
    if pickxy == 'Longitude':
        if row[pickxy] == 0 and stopid in stops_latlong_dict.keys():
            return stops_latlong_dict[stopid][0]
        else:
            return row[pickxy]
    if pickxy == 'Latitude':
        if row[pickxy] == 0 and stopid in stops_latlong_dict.keys():
            return stops_latlong_dict[stopid][1]
        else:
            return row[pickxy]

# Runs function
trc['X'] = trc.apply(lambda row: getmissingxyvalues(row,'Longitude'), axis=1)
trc['Y'] = trc.apply(lambda row: getmissingxyvalues(row,'Latitude'), axis=1)

# Creates a function that returns the stop name from Spatial Data Store
def getstopname(row):
    stopid = row['PointID']
    if stopid in stops_latlong_dict.keys():
        return stops_latlong_dict[stopid][2]
    else:
        return None

# Runs function
trc['StopName'] = trc.apply(lambda row: getstopname(row), axis=1)

# Join ptp to trc
ptp_join = ptp.loc[:,['TraceID','PatternName']].drop_duplicates(subset =['TraceID']).set_index('TraceID')
trc_joined = trc.join(ptp_join, on = 'TraceID')

output = r"G:\01_Projects\TransitServicePlanning\CorridorSpeedAnalysis\02_OtherData\Working\Scripting\trc_join_2019.csv"
trc_joined.to_csv(output)
