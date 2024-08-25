import os

import geopandas
import matplotlib.pyplot as plt
import streamlit as st

output_directory_base = "data/parques_nacionales/"
name = "data_parques"

# Load files
df = geopandas.read_file(os.path.join(output_directory_base, name + ".shp"))
df_demo = geopandas.read_file("data/demo_data/doc.kml")

df_kms = df.to_crs("EPSG:32633")
demo_geometry_kms = df_demo.to_crs("EPSG:32633")

distance = df_kms.geometry.distance(demo_geometry_kms.iloc[0].geometry) / 1000
df_kms["distance_in_kms"] = distance
close_parks = df_kms[df_kms.distance_in_kms < 50]


# Plotting the data
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the parks that are within 50 km
close_parks.plot(ax=ax, color="green", label="Parks within 50 km")

# Plot the rest of the parks
df_kms.plot(ax=ax, color="lightgrey", label="Other Parks", alpha=0.5)

# Plot the demo point
demo_geometry_kms.plot(ax=ax, color="red", label="Demo Point", markersize=100)

# Set the title and labels
ax.set_title("National Parks within 50 km of Demo Point", fontsize=15)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# Add a legend
ax.legend()

# Display the plot in Streamlit
st.pyplot(fig)

# Optionally, display the DataFrame of close parks
st.write(close_parks[["NOMBRE"]])
