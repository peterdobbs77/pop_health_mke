import requests
import json
import pandas as pd
import numpy as np
import shapefile
from geopy.geocoders import Nominatim
from matplotlib import pyplot as plt
from shapely.geometry import Point, Polygon
from descartes.patch import PolygonPatch


def plot_locations_on_mke_ald_map(loc_bbox):
    # Initialize shape file for Milwaukee Aldermanic Districts
    ald_shp = shapefile.Reader("./shape/ald2018/alderman")

    fig = plt.figure(figsize=(12, 10))
    plt.title(df.columns[0])
    ax = plt.axes()
    ax.set_aspect('equal')

    for i, shape in enumerate(ald_shp.shapes()):
        # define polygon fill color (facecolor) RGB values:
        R = 1
        G = 1
        B = 0.2
        # check number of parts (could use MultiPolygon class of shapely?)
        nparts = len(shape.parts)  # total parts
        if nparts == 1:
            polygon = Polygon(shape.points)
            patch = PolygonPatch(polygon, facecolor=[
                                 R, G, B], alpha=1.0, zorder=2)
            ax.add_patch(patch)
        else:  # loop over parts of each shape, plot separately
            for ip in range(nparts):  # loop over parts, plot separately
                i0 = shape.parts[ip]
                if ip < nparts-1:
                    i1 = shape.parts[ip+1]-1
                else:
                    i1 = len(shape.points)
                polygon = Polygon(shape.points[i0:i1+1])
                patch = PolygonPatch(polygon, facecolor=[
                                     R, G, B], alpha=1.0, zorder=2)
                ax.add_patch(patch)
        # annotate the shape with aldermanic district number
        center_x = shape.bbox[0]+((shape.bbox[2]-shape.bbox[0])/2)
        center_y = shape.bbox[1]+((shape.bbox[3]-shape.bbox[1])/2)
        ax.annotate(ald_shp.record(i)[1], xy=(center_x, center_y), color='tan',
                    ha='center', va='center', fontsize=21)

    for bbox in loc_bbox:
        p1 = Point(bbox[0], bbox[2])
        p2 = Point(bbox[1], bbox[2])
        p3 = Point(bbox[0], bbox[3])
        p4 = Point(bbox[1], bbox[3])
        pointList = [p1, p2, p3, p4]
        polygon = Polygon([[p.x, p.y] for p in pointList])
        patch = PolygonPatch(polygon, facecolor=[
                             0.1, 1, 1], alpha=1.0, zorder=2)
        ax.scatter(patch)

    plt.xlim(ald_shp.bbox[0], ald_shp.bbox[2])
    plt.ylim(ald_shp.bbox[1], ald_shp.bbox[3])
    plt.axis('off')
    plt.show()
    fig.savefig('./images/loc_on_2018_alddist.png')


# Initialize geolocator tool that uses OpenMapData
geolocator = Nominatim(user_agent="App_Name")
# API call to Open MKE Data for liquor license data
url = "https://data.milwaukee.gov/api/3/action/datastore_search?resource_id=45c027b5-fa66-4de2-aa7e-d9314292093d&limit=5"
r = requests.get(url).json()
# print(json.dumps(r, indent=4))
print('Data query success:', r['success'])

if(not r['success']):
    exit()

# If data query is successful, let's play with the data!
data = r['result']
df = pd.DataFrame(data['records'])
df['CITY'] = "Milwaukee, WI"  # add city, state to help geo location
# print(df)

address = df[['HOUSE_NR', 'SDIR', 'STREET', 'STTYPE', 'CITY']].apply(
    lambda x: ' '.join(x), axis=1)
# print(address)

points = []
for loc in address:
    geoloc = geolocator.geocode(loc)
    print(geoloc.raw)
    # bounding_box = geoloc.raw['boundingbox']
    # lat_long_bbox.append(bounding_box)
    points.append(Point(geoloc.longitude, geoloc.latitude))

print(points)

plot_locations_on_mke_ald_map(points)
