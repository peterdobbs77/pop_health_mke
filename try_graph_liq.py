import requests
import json
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from matplotlib import pyplot as plt
from shapely.geometry import Point, Polygon

# API call to Open MKE Data for liquor license data
url = "https://data.milwaukee.gov/api/3/action/datastore_search?resource_id=45c027b5-fa66-4de2-aa7e-d9314292093d&limit=5"
r = requests.get(url).json()
print(json.dumps(r, indent=4))
print('Data query success:', r['success'])

if(not r['success']):
    exit()

# If data query is successful, let's play with the data!
data = r['result']
df = pd.DataFrame(data['records'])
# print(df)

pol_dist = df[['POLICE_DISTRICT']]
ald_dist = df[['ALDERMANIC_DISTRICT']]
address = df[['HOUSE_NR', 'SDIR', 'STREET', 'STTYPE']].apply(
    lambda x: ' '.join(x), axis=1)
# print(address)


fig = plt.figure()
plt.title('MKE Liqour Licenses')
ax = plt.axes()
ax.set_aspect('equal')

geolocator = Nominatim(user_agent="App_Name")
pts = []
for loc in address:
    geoloc = geolocator.geocode(loc)
    pts.append(Point((geoloc.longitude, geoloc.latitude))
