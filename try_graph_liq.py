import requests
import json
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from matplotlib import pyplot as plt

# API call to Open MKE Data for liquor license data
url = "https://data.milwaukee.gov/api/3/action/datastore_search?resource_id=45c027b5-fa66-4de2-aa7e-d9314292093d&limit=200"
r = requests.get(url).json()
# print(json.dumps(r, indent=4))
print('Data query success:', r['success'])

if(not r['success']):
    exit()

# If data query is successful, let's play with the data!
data = r['result']
df = pd.DataFrame(data['records'])
# print(df)

address = df[['HOUSE_NR', 'SDIR', 'STREET', 'STTYPE']].apply(
    lambda x: ' '.join(x), axis=1)
# print(address)


geolocator = Nominatim(user_agent="App_Name")
lat_long = []
for loc in address:
    geoloc = geolocator.geocode(loc)
    lat_long.append(geoloc.raw)

print(lat_long)
geolocations = pd.DataFrame(lat_long)

fig = plt.figure(figsize=(12, 10))
plt.title('MKE Liqour Licenses')
plt.scatter(geolocations['lon'], geolocations['lat'])
plt.show()
fig.savefig('./images/liqlic.png')
