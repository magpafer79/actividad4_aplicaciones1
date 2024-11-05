import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import json

# Cargar los datos (ajusta la ruta de tu archivo)
data = pd.read_excel('archivo.xlsx')
data['FECHA DEFUNCIÓN'] = pd.to_datetime(data['FECHA DEFUNCIÓN'], errors='coerce')

# Filtrar datos para el año 2021 y 2020
data_2021 = data[data['FECHA DEFUNCIÓN'].dt.year == 2021]
data_2020 = data[data['FECHA DEFUNCIÓN'].dt.year == 2020]

# Preparar datos para el gráfico de mapa
dept_deaths = data_2021[data_2021['COVID-19'] == 'CONFIRMADO'].groupby('DEPARTAMENTO').size().reset_index(name='deaths')

# Cargar el archivo GeoJSON con los límites de los departamentos de Colombia
with open("colombia_departments.geojson", "r", encoding="utf-8") as file:
    colombia_geojson = json.load(file)

# Crear el gráfico de mapa utilizando el GeoJSON
map_chart = px.choropleth(
    dept_deaths,
    geojson=colombia_geojson,
    locations='DEPARTAMENTO',
    featureidkey="properties.NOMBRE_DPT",  # Esto debe coincidir con la clave en el archivo geojson
    color='deaths',
    hover_name='DEPARTAMENTO',
    title="Total COVID-19 Deaths by Department (2021)"
)

# Configuración del mapa centrado en Colombia
map_chart.update_geos(fitbounds="locations", visible=False)

# Preparar datos para el gráfico de barras (Top 5 ciudades con mayor número de muertes confirmadas)
city_deaths = data_2021[data_2021['COVID-19'] == 'CONFIRMADO'].groupby('MUNICIPIO').size().nlargest(5).reset_index(
    name='deaths')
bar_chart = px.bar(
    city_deaths,
    x='deaths',
    y='MUNICIPIO',
    orientation='h',
    title="Top 5 Cities by COVID-19 Deaths (2021)"
)

# Preparar datos para el gráfico circular de casos (confirmados, sospechosos, descartados)
case_status_counts = data_2021['COVID-19'].value_counts().reset_index()
case_status_counts.columns = ['Case Status', 'Count']
pie_chart = px.pie(
    case_status_counts,
    names='Case Status',
    values='Count',
    title="COVID-19 Case Status Distribution (2021)"
)

# Preparar datos para el gráfico de líneas de muertes por mes para 2020 y 2021
monthly_deaths_2020 = data_2020[data_2020['COVID-19'] == 'CONFIRMADO'].groupby(
    data_2020['FECHA DEFUNCIÓN'].dt.to_period('M')).size().reset_index(name='deaths')
monthly_deaths_2020['Year'] = 2020
monthly_deaths_2021 = data_2021[data_2021['COVID-19'] == 'CONFIRMADO'].groupby(
    data_2021['FECHA DEFUNCIÓN'].dt.to_period('M')).size().reset_index(name='deaths')
monthly_deaths_2021['Year'] = 2021

# Combinar los datos de ambos años
monthly_deaths = pd.concat([monthly_deaths_2020, monthly_deaths_2021])
monthly_deaths['FECHA DEFUNCIÓN'] = monthly_deaths[
    'FECHA DEFUNCIÓN'].dt.to_timestamp()  # Convertir a timestamp para la gráfica

# Crear el gráfico de línea
line_chart = px.line(
    monthly_deaths,
    x='FECHA DEFUNCIÓN',
    y='deaths',
    color='Year',
    title="Monthly COVID-19 Deaths (2020 vs 2021)"
)

# Preparar datos para el gráfico de histograma de edades quinquenales en 2020
# Convertir la columna de edad en números y luego clasificar en grupos quinquenales
data_2020['EDAD FALLECIDO'] = data_2020['EDAD FALLECIDO'].str.extract('(\\d+)').astype(float).squeeze()
data_2020['Age Group'] = pd.cut(
    data_2020['EDAD FALLECIDO'],
    bins=[0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 79, 84, 89, float('inf')],
    labels=["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44",
            "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85-89", "90+"]
)

# Crear el gráfico de histograma
histogram_chart = px.histogram(
    data_2020[data_2020['COVID-19'] == 'CONFIRMADO'],
    x='Age Group',
    title="Frequency of COVID-19 Deaths by Age Group (2020)",
    category_orders={"Age Group": ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44",
                                   "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85-89",
                                   "90+"]}
)

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Configurar el layout con el mapa, gráfico de barras, gráfico circular, gráfico de línea y gráfico de histograma
app.layout = html.Div([
    html.H1("COVID-19 Dashboard - Mapa de Muertes por COVID-19 en 2021"),

    # Mapa
    dcc.Graph(figure=map_chart),

    # Gráfico de barras horizontal
    dcc.Graph(figure=bar_chart),

    # Gráfico circular
    dcc.Graph(figure=pie_chart),

    # Gráfico de línea
    dcc.Graph(figure=line_chart),

    # Gráfico de histograma
    dcc.Graph(figure=histogram_chart)
])

# Ejecutar el servidor Dash
if __name__ == '__main__':
    app.run_server(debug=False)
