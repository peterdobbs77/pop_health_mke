import requests
import json
import pandas as pd
import numpy as np
import shapefile
from geopy.geocoders import Nominatim
from matplotlib import pyplot as plt
from shapely.geometry import Point, Polygon
from descartes.patch import PolygonPatch
from datetime import datetime


def plot_shape(shp_path):
    shp = shapefile.Reader(shp_path)

    fig = plt.figure(figsize=(5, 5))
    plt.title('City of Milwaukee')
    ax = plt.axes()
    ax.set_aspect('equal')

    for i, shape in enumerate(shp.shapes()):
        # check number of parts (could try MultiPolygon class of shapely?)
        nparts = len(shape.parts)  # total parts
        if nparts == 1:
            polygon = Polygon(shape.points)
            patch = PolygonPatch(polygon, facecolor=[
                                 1, 1, 1], alpha=1.0, zorder=0)
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
                                     1, 1, 1], alpha=1.0, zorder=0)
                ax.add_patch(patch)
        # annotate the shape with label in data
        # center_x = shape.bbox[0]+((shape.bbox[2]-shape.bbox[0])/2)
        # center_y = shape.bbox[1]+((shape.bbox[3]-shape.bbox[1])/2)
        # ax.annotate(shp.record(i)[1], xy=(center_x, center_y), color='tan',
        #             ha='center', va='center', fontsize=21)

    # SET VIEW TO WITHIN EXPECTED BOUNDS OF CITY OF MKE
    plt.xlim(shp.bbox[0], shp.bbox[2])
    plt.ylim(shp.bbox[1], shp.bbox[3])

    plt.axis('on')
    plt.show()
    fig.savefig(
        './output/plot_shape_{}.png'.format(datetime.timestamp(datetime.now())))


def plot_locations_on_mke_map(points):
    print('..start plot generation..')
    # Initialize shape file for Milwaukee County Municipal Boundaries
    shp = shapefile.Reader("./shape/citylimit/citylimit")

    fig = plt.figure(figsize=(5, 5))
    plt.title('City of Milwaukee')
    ax = plt.axes()
    ax.set_aspect('equal')

    for i, shape in enumerate(shp.shapes()):
        # check number of parts (could try MultiPolygon class of shapely?)
        nparts = len(shape.parts)  # total parts
        if nparts == 1:
            polygon = Polygon(shape.points)
            patch = PolygonPatch(polygon, facecolor=[
                                 1, 1, 1], alpha=1.0, zorder=0)
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
                                     1, 1, 1], alpha=1.0, zorder=0)
                ax.add_patch(patch)
        # annotate the shape with label in data
        # center_x = shape.bbox[0]+((shape.bbox[2]-shape.bbox[0])/2)
        # center_y = shape.bbox[1]+((shape.bbox[3]-shape.bbox[1])/2)
        # ax.annotate(shp.record(i)[1], xy=(center_x, center_y), color='tan',
        #             ha='center', va='center', fontsize=21)

    # ADD ADDRESS GEOCOORDINATES AS POINTS
    # plt.scatter(points.x, points.y, s=20, c="cyan")

    # SET VIEW TO WITHIN EXPECTED BOUNDS OF CITY OF MKE
    # plt.xlim(shp.bbox[0], shp.bbox[2])
    # plt.ylim(shp.bbox[1], shp.bbox[3])

    #
    plt.axis('on')
    plt.show()
    fig.savefig('./output/{}.png'.format(datetime.timestamp(datetime.now())))


plot_shape('./shape/citylimit/citylimit')
exit()

useApi = False
limitApi = 200

df = pd.read_csv('./data/liquorlicenses.csv')

if (useApi):
    resourceId = '45c027b5-fa66-4de2-aa7e-d9314292093d'
    # API call to Open MKE Data for liquor license data
    url = "https://data.milwaukee.gov/api/3/action/datastore_search?resource_id={}&limit={}".format(resourceId,
                                                                                                    limitApi)
    r = requests.get(url).json()
    # print(json.dumps(r, indent=4))
    print('Data query success:', r['success'])

    if(not r['success']):
        exit()

    # If data query is successful, let's play with the data!
    data = r['result']
    df = pd.DataFrame(data['records'])

df['CITY'] = "Milwaukee, WI"  # add city, state to help geo location
print(df.head())

# df_grouped = df[['']]

address = df[['HOUSE_NR', 'SDIR', 'STREET', 'STTYPE', 'CITY']].apply(
    lambda x: ' '.join(map(str, x)), axis=1)
print(address)


# Initialize geolocator tool that uses OpenMapData
geolocator = Nominatim(user_agent="App_Name5")
coords = []
points = []
for i, loc in enumerate(address):
    if(i > limitApi):
        break

    geoloc = geolocator.geocode(loc)
    if(geoloc is None):
        print(i, '..error: no location found for input address! ({})'.format(loc))
        coords.append({'lat': '',
                       'lon': ''})
        points.append({'x': '',
                       'y': ''})
        continue

    # print(geoloc.raw)
    # print(i, ":", (geoloc.longitude, geoloc.latitude))
    coords.append({'lat': geoloc.latitude,
                   'lon': geoloc.longitude})
    points.append({'x': (geoloc.longitude*10000.0)+3600000,
                   'y': geoloc.latitude*10000.0})

crds = pd.DataFrame(coords)
df['LAT'] = crds['lat']
df['LON'] = crds['lon']
df.to_csv('./output/liquorlicenses_mod.csv')

pts = pd.DataFrame(points)
print(pts)

plot_locations_on_mke_map(pts)
