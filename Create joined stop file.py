# Create joined stop file

import pandas as pd

loc = r"C:\Users\1280530\GIS\GTFS to Feature Class\02_OtherData\nyc-bus-company-gtfs\\"
components = ['agency.txt','calendar.txt','calendar_dates.txt','routes.txt','shapes.txt','stop_times.txt','stops.txt','trips.txt']

routes = pd.read_csv(loc + r'routes.txt')
stops = pd.read_csv(loc + r'stops.txt')
trips = pd.read_csv(loc + r'trips.txt')
stoptimes = pd.read_csv(loc + r'stop_times.txt')

# Get a list of routes
# Find each unique trip_id, route_id, and direction in trips
tripids = trips.groupby(['trip_id','route_id','direction_id']).size().reset_index()

# Find unique route_ids and directions
routeids = trips.groupby(['route_id','direction_id']).size().reset_index()

# Join 

# A function that pulls a list of trips for each route and direction
def listoftrips(df, route, dir):
    filtered = df.loc[(['route_id'] == route) & (['direction_id'] == dir)]
    return filtered[trip_id].unique()

# A function that
def pull
    stoptimedf[[]]

