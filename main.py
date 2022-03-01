# Aplicación desarrollada en Streamlit para visualización de datos sobre la red vial de Costa Rica
# Autor: Manuel Morales Chaves (manuel.moraleschaves@ucr.ac.cr)
# Fecha de creación: 2022-02-26


# Se importan los paquetes necesarios

import requests

import math

import streamlit as st

import pandas as pd
import geopandas as gpd

import plotly.express as px

import folium
from streamlit_folium import folium_static



############################
# Configuración de la página
############################

st.set_page_config(layout="wide")



#######################################
# TÍTULO Y DESCRIPCIÓN DE LA APLICACIÓN
#######################################

st.title('Visualización de datos sobre la red vial de Costa Rica')
st.markdown('Esta aplicación presenta visualizaciones tabulares, gráficas y geoespaciales sobre la red vial de Costa Rica a partir de las siguientes capas Web Feature Service (WFS) publicadas por el Instituto Geográfico Nacional (IGN) en el [Sistema Nacional de Información Territorial (SNIT)](https://www.snitcr.go.cr/):')
st.markdown('* Límite cantonal 1:5000')
st.markdown('* Red vial 1:200000')
st.markdown('El usuario debe seleccionar la categoría de vía que desee y la aplicación mostrará un conjunto de tablas, gráficos y mapas correspondientes a la longitud y la densidad de la red vial para la **categoría seleccionada**.')
st.markdown('El código fuente de esta aplicación se encuentra alojado en el siguiente repositorio de [GitHub](https://github.com/manuel-moraleschaves/PF3311-proyecto).')



#############
# 1. ENTRADAS
#############

#
# Capa Límite cantonal 1:5000
#

# Solicitud de capa WFS del límite cantonal mediante GET, para retornarse como JSON

# Parámetros de la solicitud
params = dict(service='WFS',
              version='2.0.0', 
              request='GetFeature', 
              typeName='IGN_5:limitecantonal_5k',
              srsName='urn:ogc:def:crs:EPSG::5367',
              outputFormat='json')

# Solicitud
response = requests.Request("GET", "https://geos.snitcr.go.cr/be/IGN_5/wfs", params=params).prepare().url

# Leer datos del URL
cantones = gpd.read_file(response)

# Seleccionar únicamente las columnas necesarias para el análisis
cantones = cantones[["canton", "geometry"]].copy()

# Se calcula el área de cada cantón
cantones['area_km2'] = cantones.area / 1000000 # se divide para convertirlo a km2


#
# Capa Red vial 1:200000
#

# Solicitud de capa WFS de la red vial mediante GET, para retornarse como JSON

# Parámetros de la solicitud
params = dict(service='WFS',
              version='2.0.0', 
              request='GetFeature', 
              typeName='IGN_200:redvial_200k',
              srsName='urn:ogc:def:crs:EPSG::5367',
              outputFormat='json')

# Solicitud
response = requests.Request("GET", "https://geos.snitcr.go.cr/be/IGN_200/wfs", params=params).prepare().url

# Leer datos del URL
red_vial = gpd.read_file(response)

# Seleccionar únicamente las columnas necesarias para el análisis
red_vial = red_vial[["categoria", "geometry"]].copy()


#
# Especificación del filtro
#

# Categoría
lista_categorias = red_vial.categoria.unique().tolist()
lista_categorias.sort()
filtro_categoria = st.sidebar.selectbox('Seleccione la categoría de la red vial', lista_categorias)
