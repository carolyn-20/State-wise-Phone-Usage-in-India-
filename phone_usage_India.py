import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
import streamlit as st
import folium
import json
from streamlit_folium import folium_static


#DATABASE:

host = 'localhost'
port = 3306
user = 'root'
password = 'carolyn'
database = 'phone_usage_india'

conn = mysql.connector.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

cursor = conn.cursor()

query = 'SELECT * FROM dataset'

cursor.execute(query)

result = cursor.fetchall()

for row in result:
    print(row)

cursor.close()
conn.close()

columns = [i[0] for i in cursor.description]

cursor.close()
conn.close()

#PREPROCESSING:

df = pd.DataFrame(result, columns = columns)

df.dropna(inplace = True)

data =  df.drop(['Primary Use','User ID','Phone Brand','OS', 'Gender'], axis  = 1)

from sklearn.model_selection import train_test_split
X = data.drop(['Location'], axis  = 1)
y = data['Location']

data['Location'].value_counts()

user_data = {k.strip().title(): v for k, v in data['Location'].value_counts().to_dict().items()}


#MAP

state_coords = {
   'Andhra Pradesh': [15.9129, 79.73999],
    'Tamil Nadu': [11.1271, 78.6569],
    'Karnataka': [15.3173, 75.7139],
    'Maharashtra': [19.7515, 75.7139],
    'Uttar Pradesh': [27.5934, 81.3792],
    'West Bengal': [22.9868, 87.8550],
    'Gujarat': [22.2587, 71.1924],
    'Bihar': [25.0961, 85.3131],
    'Rajasthan': [27.0238, 74.2179],
    'Punjab': [31.1471, 75.3412],
    'Haryana': [29.0588, 76.0856],
    'Kerala': [10.8505, 76.2711],
    'Madhya Pradesh': [23.4735, 77.9478],
    'Odisha': [20.9517, 85.0985],
    'Telangana': [17.1232, 79.2085],
    'Chhattisgarh': [21.2787, 81.8661],
    'Jharkhand': [23.6100, 85.2799],
    'Assam': [26.2006, 92.9376],
    'Himachal Pradesh': [32.0637, 77.1734],
    'Jammu and Kashmir': [33.7783, 76.5762],
    'Uttarakhand': [30.0668, 79.0193],
    'Goa': [15.2993, 74.1240],
    'Tripura': [23.9400, 91.9882],
    'Meghalaya': [25.4670, 91.3662],
    'Nagaland': [26.1584, 94.5624],
    'Arunachal Pradesh': [27.0663, 93.6050],
    'Sikkim': [27.5330, 88.5122],
    'Manipur': [24.6637, 93.9063],
    'Mizoram': [23.1645, 92.9376],
    'Karnataka': [15.3173, 75.7139],
    'Lakshadweep': [10.5635, 72.6349],
    'Andaman and Nicobar Islands': [11.7401, 92.6586]
}

city_to_state = {
    'Mumbai': 'Maharashtra',
    'Pune': 'Maharashtra',
    'Delhi': 'Delhi',
    'Ahmedabad': 'Gujarat',
    'Jaipur': 'Rajasthan',
    'Lucknow': 'Uttar Pradesh',
    'Kolkata': 'West Bengal',
    'Bangalore': 'Karnataka',
    'Chennai': 'Tamil Nadu',
    'Hyderabad': 'Telangana',
}

data['State'] = data['Location'].map(city_to_state)

data = data.dropna(subset=['State'])

user_data = data['State'].value_counts().to_dict()

print(user_data)



#India map
def india_map_with_geojson(geojson_file_path, state_name=None):
    india_map = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="OpenStreetMap")

    with open(geojson_file_path, 'r') as f:
        geojson_data = json.load(f)

    for state, coords in state_coords.items():
        user_count = user_data.get(state, 0)  
        folium.Marker(
            location=coords,
            popup=f"<b>{state}</b><br>Users: {user_count}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(india_map)

    if state_name and state_name in state_coords:
        india_map.location = state_coords[state_name]
        india_map.zoom_start = 7

    return india_map

st.title('INDIA MAP')

state_option = st.sidebar.selectbox('Select a State:', [''] + list(state_coords.keys()))

geojson_file_path = r'C:\Users\Hp\OneDrive\Documents\states_india.geojson'
india_map = india_map_with_geojson(geojson_file_path, state_option)

folium_static(india_map)

#SIDEBAR:

st.sidebar.title('OPEN')

button_heatmap = st.sidebar.button('Heatmap')
button_hist = st.sidebar.button('Histogram')


def display_heatmap():
    hm = pd.get_dummies(data['Location'])
    corr = hm.corr()
    fig = plt.figure(figsize = (25, 20))
    sns.heatmap(corr, annot = True, annot_kws = {'size':15}, cmap = 'coolwarm')
    plt.title('HEATMAP OF CORRELATION MATRIX', fontweight = 'bold', fontsize = 50)
    st.pyplot(fig)
    
def display_hist():
    hist = plt.figure(figsize=(10, 10))
    data.hist(ax=hist.gca(), bins=30)
    hist.suptitle('HISTOGRAM', fontsize = 25, fontweight = 'bold')
    st.pyplot(hist)
    
if button_heatmap:
    display_heatmap()
if button_hist:
    display_hist()

#BACKGROUND:

def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background('https://www.pixelstalk.net/wp-content/uploads/2016/06/World-map-background-wallpapers-HD.jpg')


