import requests
import json
import pandas as pd
import numpy as np


# API call to Open MKE Data for liquor license data
url = "https://data.milwaukee.gov/api/3/action/datastore_search?resource_id=45c027b5-fa66-4de2-aa7e-d9314292093d"
r = requests.get(url).json()
#print('Data query success:', r['success'])

# If data query is successful, let's play with the data!
if (r['success']):
    #print(json.dumps(r, indent=4))
    data = r['result']
    df = pd.DataFrame(data['records'])
    print(df)





#from geopy.geocoders import Nominatim
