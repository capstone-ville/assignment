#!/usr/bin/env python
# coding: utf-8

# ## Introduction

# In this assignment I'll be using the following scenario: A boutique hotel in Madrid has decided to expand it's precence to Paris and wants to open up a new hotel in central Paris.
# 
# The hotel wants to make sure that there are similar characteristics in the neighbourhood in Paris compared to its central Madrid location, so that the hotel will attract customers who look for similar experiences.
# 
# In order to find out which area satisfies these requirements, the central areas of the two cities will be compared using K-Means clustering technique.

# ## Data

# This analysis will use data obtained mainly from Geopy, Wikipedia and Foursquare. 
# 

# In[1]:


# importing required modules
import pandas as pd
import requests


# In[2]:


# importing Madrid neighborhoods
url = 'https://en.wikipedia.org/wiki/List_of_wards_of_Madrid'
results = requests.get(url).text
df = pd.read_html(results, header=0, attrs={"class":"wikitable sortable"})[0]
df = df[0:128]

df.drop(['Number','Image'],axis=1,inplace=True)

df.rename(columns={'Name':'Neighborhood'},inplace=True)
df = df.groupby(['District'])['Neighborhood'].apply(','.join).reset_index()

df_raw = df.copy()
df_raw.head()

df.head()

df_rev = df_raw.set_index('District').Neighborhood.str.split(',', expand=True).stack().reset_index('District')
df_rev.rename(columns={0:'Neighborhood'},inplace=True)
df_rev.Neighborhood = df_rev.Neighborhood.astype(str) + ', Madrid, ES'
mad = df_rev.copy()
mad.reset_index(drop=True, inplace=True)

mad

# # filtering only the area of the hotel in Madrid
mad = mad.loc[mad['Neighborhood'] == 'Atocha, Madrid, ES']
mad.reset_index(drop=True, inplace=True)
mad


# In[50]:


# importing Paris neighborhoods
url = 'https://en.wikipedia.org/wiki/Arrondissements_of_Paris#Arrondissements'
results = requests.get(url).text
df = pd.read_html(results, header=0, attrs={"class":"wikitable sortable"})[0]

df.drop(['Area (km2)','Population(March 1999 census)','Population(July 2005 estimate)','Density (2005)(inhabitants per km2)','Peak of population','Mayor'],
        axis=1,inplace=True)
df.rename(columns={'Arrondissement (R for Right Bank, L for Left Bank)':'District','Name':'Neighborhood'},inplace=True)

df.Neighborhood = df.Neighborhood.astype(str) + ', Paris, FR'
pa = df.copy()

pa


# In[51]:


# merging dataframes for next steps
df2 = mad.append(pa)
df2.reset_index(drop=True, inplace=True)
df2


# ## Analysis

# In[5]:


#importing modules
import numpy as np
from pandas.io.json import json_normalize
from geopy.geocoders import Nominatim
from sklearn.cluster import KMeans

import folium
import matplotlib.cm as cm
import matplotlib.colors as colors


# In[6]:


# @hidden_cell
CLIENT_ID = 'useyourown' # your Foursquare ID
CLIENT_SECRET = 'useyourown' # your Foursquare Secret
VERSION = '20190112' # Foursquare API version

radius = 500
LIMIT = 100

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[7]:


df2.shape


# In[17]:


def findlat(row):
    geolocator = Nominatim(user_agent="my-app")
    location = geolocator.geocode(row['Neighborhood'], timeout=10)
    lat = location.latitude
    return lat


# In[18]:


def findlng(row):
    geolocator = Nominatim(user_agent="my-app")
    location = geolocator.geocode(row['Neighborhood'], timeout=10)
    lng = location.longitude
    return lng


# In[52]:


# finding latitude and longitude per each neighborhood in dataset
df2['lat'] = df2.apply(findlat, axis=1)
df2['lng'] = df2.apply(findlng, axis=1)
print(df2.shape)
df2.head()


# In[53]:


# function to find venues through Foursquare API
def getNearbyVenues(names, latitudes, longitudes, radius=800):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        # print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],
#             v['venue']['id'],
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue',           
                  'Venue Latitude', 
                  'Venue Longitude',
#                   'Venue ID',
                  'Venue Category']
    
    return(nearby_venues)


# In[54]:


# finding venues for each neighborhood
venues = getNearbyVenues(names=df2['Neighborhood'],latitudes=df2['lat'],longitudes=df2['lng'])
venues.head()


# In[55]:


venues.shape


# In[56]:


# venue categories in the dataset venues
print('There are {} uniques categories.'.format(len(venues['Venue Category'].unique())))


# In[57]:


# venue categories in Atocha only
atocha = venues.loc[venues['Neighborhood'] == 'Atocha, Madrid, ES'].copy()
print('There are {} uniques categories.'.format(len(atocha['Venue Category'].unique())))


# In[58]:


atocha.shape


# In[59]:


atocha['Venue Category'].unique()


# In[60]:


# storing Atocha area coordinates into variables for data visualization
geolocator = Nominatim(user_agent="my-app")
location = geolocator.geocode('Atocha, Madrid, ES')
lat_mad = location.latitude
lng_mad = location.longitude
print(lat_mad,lng_mad)


# In[61]:


# visualizing location of venue in a radius of 1000 meters from the coordinates of Atocha area
atocha_map = folium.Map(location=[lat_mad, lng_mad], zoom_start=15)
folium.Circle([lat_mad, lng_mad],
              radius=1000,
              color='red').add_to(atocha_map)

for lat, lon, poi in zip(atocha['Venue Latitude'], atocha['Venue Longitude'], atocha['Venue Category']):
    label = folium.Popup(str(poi), parse_html=True)
    folium.CircleMarker(
        [float(lat), float(lon)],
        # radius=res_count,
        popup=label,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.7).add_to(atocha_map)

atocha_map


# ## One Hot encoding

# In[62]:


# one hot encoding
df_onehot = pd.get_dummies(venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
df_onehot['Neighborhood'] = venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [df_onehot.columns[-1]] + list(df_onehot.columns[:-1])
df_onehot = df_onehot[fixed_columns]

df_onehot.head()


# In[63]:


df_grouped = df_onehot.groupby('Neighborhood').mean().reset_index()
print(df_grouped.shape)
df_grouped


# In[35]:


# function to return the most common venues
def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[64]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = df_grouped['Neighborhood']

for ind in np.arange(df_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(df_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted


# In[74]:


kclusters = 3 

df_grouped_clustering = df_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(df_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_


# In[75]:


df_merged = df2

# add clustering labels
df_merged['Cluster Labels'] = kmeans.labels_

# merge df_merged with neighborhoods_venues_sorted dataframe to add latitude/longitude for each neighborhood
df_merged = df_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighborhood')

df_merged


# ## Results

# In[76]:


df_merged.loc[df_merged['Cluster Labels'] == 1]


# In[80]:


# venue categories in Batignolles-Monceau area in Paris only
batignolles = venues.loc[venues['Neighborhood'] == 'Batignolles-Monceau, Paris, FR'].copy()
print('There are {} uniques categories.'.format(len(atocha['Venue Category'].unique())))


# In[81]:


batignolles.shape


# In[82]:


batignolles['Venue Category'].unique()


# It seems that Batignolles-Monceau has the same variety of venue categories.

# Let's visualize the **location** of each venue on a map of the Batignolles-Monceau area.

# In[84]:


# storing Batignolles-Monceau district coordinates into variables for data visualization
geolocator = Nominatim(user_agent="my-app")
location = geolocator.geocode('Batignolles-Monceau, Paris, FR')
lat_ba = location.latitude
lng_ba = location.longitude
print(lat_ba,lng_ba)


# In[86]:


# visualizing location of venues in a radius of 1000 meters from the coordinates of Batignolles-Monceau district
batignolles_map = folium.Map(location=[lat_ba, lng_ba], zoom_start=15)
folium.Circle([lat_ba, lng_ba],
              radius=1000,
              color='red').add_to(batignolles_map)

for lat, lon, poi in zip(batignolles['Venue Latitude'], batignolles['Venue Longitude'], batignolles['Venue Category']):
    label = folium.Popup(str(poi), parse_html=True)
    folium.CircleMarker(
        [float(lat), float(lon)],
        # radius=res_count,
        popup=label,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.7).add_to(batignolles_map)

batignolles_map


# In[ ]:




