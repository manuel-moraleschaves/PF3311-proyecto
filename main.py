# Aplicación desarrollada en Streamlit para visualización de datos sobre la red vial de Costa Rica
# Autor: Manuel Morales Chaves (manuel.moraleschaves@ucr.ac.cr)
# Fecha de creación: 2022-02-26

import math

import streamlit as st

import pandas as pd
import geopandas as gpd

import plotly.express as px

import folium
from streamlit_folium import folium_static

#
# Configuración de la página
#
st.set_page_config(layout="wide")


#
# TÍTULO Y DESCRIPCIÓN DE LA APLICACIÓN
#

st.title('Visualización de datos sobre la red vial de Costa Rica')
st.markdown('Esta aplicación presenta visualizaciones tabulares, gráficas y geoespaciales sobre la red vial de Costa Rica a partir de las siguientes capas Web Feature Service (WFS) publicadas por el Instituto Geográfico Nacional (IGN) en el [Sistema Nacional de Información Territorial (SNIT)](https://www.snitcr.go.cr/):')
st.markdown('* Límite cantonal 1:5000')
st.markdown('* Red vial 1:200000')
st.markdown('El usuario debe seleccionar la categoría de vía que desee y la aplicación mostrará un conjunto de tablas, gráficos y mapas correspondientes a la longitud y la densidad de la red vial para la categoría seleccionada.')
