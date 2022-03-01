# Aplicación desarrollada en Streamlit para visualización de datos sobre la red vial de Costa Rica
# Autor: Manuel Morales Chaves (manuel.moraleschaves@ucr.ac.cr)
# Fecha de creación: 2022-02-26


# Se importan los paquetes necesarios

import requests

import streamlit as st

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
st.markdown('')



#############
# 1. ENTRADAS
#############

# Validación para cargar los datos de las capas WFS únicamente una vez al iniciar la aplicación
if 'datos_cargados' not in st.session_state:

    st.session_state.datos_cargados = True

    # Barra para mostrar el progreso de la carga de datos
    my_bar = st.progress(0)


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

    # Se actualiza la barra de progreso
    my_bar.progress(10)

    # Leer datos del URL y almacenarlos en Session State
    st.session_state.cantones = gpd.read_file(response)

    # Se actualiza la barra de progreso
    my_bar.progress(30)

    # Seleccionar únicamente las columnas necesarias para el análisis
    st.session_state.cantones = st.session_state.cantones[["canton", "geometry"]].copy()

    # Se calcula el área de cada cantón
    st.session_state.cantones['area_km2'] = st.session_state.cantones.area / 1000000 # se divide para convertirlo a km2

    # Se actualiza la barra de progreso
    my_bar.progress(50)


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

    # Se actualiza la barra de progreso
    my_bar.progress(60)

    # Leer datos del URL y almacenarlos en Session State
    st.session_state.red_vial = gpd.read_file(response)

    # Se actualiza la barra de progreso
    my_bar.progress(75)

    # Seleccionar únicamente las columnas necesarias para el análisis
    st.session_state.red_vial = st.session_state.red_vial[["categoria", "geometry"]].copy()

    # Se actualiza la barra de progreso
    my_bar.progress(100)
    

#
# Especificación del filtro
#

# Categoría de la red vial
lista_categorias = st.session_state.red_vial.categoria.unique().tolist()
lista_categorias.sort()
filtro_categoria = st.sidebar.selectbox('Seleccione la categoría de la red vial:', lista_categorias)



##################
# 2. PROCESAMIENTO
##################

# Filtrado
red_vial = st.session_state.red_vial[st.session_state.red_vial['categoria'] == filtro_categoria]

# Intersección entre la capa de cantones y la capa de registros de la red vial
cantones_red_vial = st.session_state.cantones.overlay(red_vial, how='intersection', keep_geom_type=False)

# Se calcula la longitud de cada red vial. Se divide entre mil para convertirlo a km
cantones_red_vial["longitud_km"] = cantones_red_vial.length / 1000

# Se agrupan los registros por cantón para sumar su longitud
cantones_red_vial = cantones_red_vial.groupby(["canton"]).longitud_km.sum()

# Se convierte la serie a Dataframe
cantones_red_vial = cantones_red_vial.reset_index() 

# Join para agregar la columna de la longitud de la red vial
cantones_red_vial = st.session_state.cantones.join(cantones_red_vial.set_index('canton'), on='canton')

# Se coloca en 0 la longitud de la red vial en los cantones que tienen nulo
cantones_red_vial["longitud_km"] = cantones_red_vial.longitud_km.fillna(0)

# Se calcula la densidad de la red vial para cada cantón
cantones_red_vial['densidad_vial'] = round(cantones_red_vial.longitud_km / cantones_red_vial.area_km2, 2) # se redondea a dos decimales



############
# 3. SALIDAS
############

#
# Tabla de cantones con longitud y densidad de la red vial
#

# Dataframe con nombre de columnas más representativo
tabla_cantones = cantones_red_vial[['canton', 'longitud_km', 'densidad_vial']].rename(columns = {'canton':'Cantón', 'longitud_km':'Longitud (km)', 'densidad_vial':'Densidad red vial'})

# Para mostrar el índice del cantón de 1 a 82
tabla_cantones.index += 1

st.header('Longitud de las vías y densidad de la red vial en cada cantón')
st.dataframe(tabla_cantones)


# Definición de columnas
col1, col2 = st.columns(2)

#
# Gráfico de barras con la longitud de la categoría de vías seleccionada 
#
with col1:

    # Dataframe filtrado para usar en graficación
    cantones_red_vial_grafico = cantones_red_vial.loc[cantones_red_vial['longitud_km'] > 0, 
                                                     ["canton", "longitud_km"]].sort_values("longitud_km", ascending=[False]).head(15)
    
    # Se establece el canton como el índice
    cantones_red_vial_grafico = cantones_red_vial_grafico.set_index('canton')  
                                                  
    st.header('Longitud de las vías')

    # Se crea y se personaliza el gráfico de barras
    fig = px.bar(cantones_red_vial_grafico, 
                labels={'canton':'Cantones de CR', 'value':'Longitud de la red vial (km)', 'variable':'Categoría de red vial'})

    fig.data[0].name = filtro_categoria
        
    fig.update_traces(hovertemplate='Cantón = %{x} <br>Longitud red vial (km) = %{y}')

    # Se muestra el gráfico
    st.plotly_chart(fig) 

#
# Gráfico de pastel con el porcentaje de red vial
# 
with col2:    

    # Dataframe filtrado para usar en graficación
    cantones_red_vial_grafico = cantones_red_vial.sort_values("longitud_km", ascending=[False]).head(15)[["canton", "longitud_km"]]

    # Se obtiene la suma de la longitud de la red vial de los 67 cantones restantes 
    suma_restantes = cantones_red_vial.sort_values("longitud_km", ascending=[True]).head(len(st.session_state.cantones) - 15).longitud_km.sum()

    # Se agrega el registro de los otros cantones al Dataframe
    cantones_red_vial_grafico.loc[-1] = ["Otros cantones", suma_restantes]

    st.header('Porcentaje de red vial')

    # Se crea y se personaliza el gráfico de pastel
    fig = px.pie(cantones_red_vial_grafico, 
                names=cantones_red_vial_grafico.canton,
                values='longitud_km')

    fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate='Cantón = %{label}<br>Longitud red vial (km) = %{value}')

    # Se muestra el gráfico
    st.plotly_chart(fig)    


#
# Mapa con las Líneas de la red vial y capa de coropletas
#

st.header('Líneas y densidad de la red vial')

# Creación del mapa base con el control de escala
m = folium.Map(location=[9.8, -84.2],
               tiles='CartoDB positron',
               width=650,
               zoom_start=8,
               control_scale=True)

# Se añade al mapa la capa de coropletas
folium.Choropleth(
    name="Densidad de la red vial",
    geo_data=st.session_state.cantones,
    data=cantones_red_vial,
    columns=['canton', 'densidad_vial'],
    bins=8,
    key_on='feature.properties.canton',
    fill_color='Reds', 
    fill_opacity=0.5, 
    line_opacity=1,
    legend_name='Densidad de la red vial',
    smooth_factor=0).add_to(m)

# Se añade al mapa la capa de la red vial
folium.GeoJson(data=red_vial, name='Líneas de la red vial').add_to(m)

# Control de capas
folium.LayerControl().add_to(m)

# Despliegue del mapa
folium_static(m)   