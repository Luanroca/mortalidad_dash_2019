
import os
import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, dash_table
from utils import preprocess, DEPT_CENTROIDS

df = preprocess()

# Aggregations
depto_agg = df.groupby(['COD_DEPARTAMENTO','DEPARTAMENTO'], dropna=False).size().reset_index(name='TOTAL_MUERTES')
mes_agg = df.groupby('MES').size().reset_index(name='TOTAL_MUERTES').sort_values('MES')
homi = df[df['ICD4'].str.startswith('X95', na=False)]
ciudad_violenta = homi.groupby(['COD_MUNICIPIO','MUNICIPIO'], dropna=False).size().reset_index(name='HOMICIDIOS')
top5_violentas = ciudad_violenta.sort_values('HOMICIDIOS', ascending=False).head(5)
ciudad_total = df.groupby(['COD_MUNICIPIO','MUNICIPIO'], dropna=False).size().reset_index(name='TOTAL')
ciudad_total = ciudad_total[ciudad_total['MUNICIPIO'].notna()]
bottom10_ciudades = ciudad_total.sort_values('TOTAL', ascending=True).head(10)
causas = df.groupby(['ICD4','CAUSA_NOMBRE'], dropna=False).size().reset_index(name='TOTAL')
top10_causas = causas.sort_values('TOTAL', ascending=False).head(10)
sexo_map = {1: 'Hombres', 2: 'Mujeres'}
df['SEXO_LABEL'] = df['SEXO'].map(sexo_map).fillna('Sin dato')
depto_sexo = df.groupby(['DEPARTAMENTO','SEXO_LABEL']).size().reset_index(name='TOTAL')
edad_agg = df.groupby('GRUPO_EDAD_LABEL').size().reset_index(name='TOTAL').sort_values('TOTAL', ascending=False)

# Figures
centroids_df = pd.DataFrame([{'COD_DEPARTAMENTO': k, 'LAT': v[0], 'LON': v[1]} for k,v in DEPT_CENTROIDS.items()])
map_df = depto_agg.merge(centroids_df, on='COD_DEPARTAMENTO', how='left')
fig_map = px.scatter_geo(map_df, lat='LAT', lon='LON', size='TOTAL_MUERTES', hover_name='DEPARTAMENTO',
                         hover_data={'TOTAL_MUERTES': True, 'LAT': False, 'LON': False},
                         projection="natural earth", title="Total de muertes por departamento (Colombia, 2019)")
fig_map.update_geos(fitbounds="locations", showcountries=True, lataxis_showgrid=True, lonaxis_showgrid=True)
fig_line = px.line(mes_agg, x='MES', y='TOTAL_MUERTES', markers=True, title="Muertes por mes (2019)")
fig_line.update_layout(xaxis_title="Mes", yaxis_title="Total de muertes")
fig_barras_viol = px.bar(top5_violentas, x='MUNICIPIO', y='HOMICIDIOS', title="Top 5 ciudades por homicidios (X95)")
fig_barras_viol.update_layout(xaxis_title="Ciudad", yaxis_title="Homicidios (X95)")
fig_pie_low = px.pie(bottom10_ciudades, names='MUNICIPIO', values='TOTAL', title="10 ciudades con menor mortalidad")
table_cols = [{"name": "Código (ICD4)", "id": "ICD4"},
              {"name": "Causa de muerte", "id": "CAUSA_NOMBRE"},
              {"name": "Total", "id": "TOTAL"}]
fig_stack = px.bar(depto_sexo, x='DEPARTAMENTO', y='TOTAL', color='SEXO_LABEL', title="Muertes por sexo y departamento", barmode='stack')
fig_stack.update_layout(xaxis_tickangle=45)
fig_hist = px.bar(edad_agg, x='GRUPO_EDAD_LABEL', y='TOTAL', title="Distribución por grupos de edad (GRUPO_EDAD1)")
fig_hist.update_layout(xaxis_title="Grupo de edad", yaxis_title="Total de muertes", xaxis_tickangle=30)

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    html.Div(className="card", children=[
        html.Div(className="title", children="Mortalidad en Colombia (2019) — Dashboard interactivo"),
        html.Div(className="subtitle", children="Fuente: DANE - Estadísticas Vitales (No fetal) 2019")
    ]),
    html.Div(className="card", children=[
        html.Div(className="title", children="Mapa por departamento"),
        dcc.Graph(figure=fig_map)
    ]),
    html.Div(className="card", children=[
        html.Div(className="title", children="Muertes por mes"),
        dcc.Graph(figure=fig_line)
    ]),
    html.Div(className="card", children=[
        html.Div(className="title", children="Top 5 ciudades con más homicidios (X95)"),
        dcc.Graph(figure=fig_barras_viol)
    ]),
    html.Div(className="card", children=[
        html.Div(className="title", children="10 ciudades con menor mortalidad"),
        dcc.Graph(figure=fig_pie_low)
    ]),
    html.Div(className="card", children=[
        html.Div(className="title", children="Top 10 causas de muerte"),
        dash_table.DataTable(
            data=top10_causas.to_dict('records'),
            columns=table_cols,
            page_size=10,
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_cell={"padding":"8px","textAlign":"left"},
            style_header={"fontWeight":"bold"}
        )
    ]),
    html.Div(className="card", children=[
        html.Div(className="title", children="Muertes por sexo por departamento"),
        dcc.Graph(figure=fig_stack)
    ]),
    html.Div(className="card", children=[
        html.Div(className="title", children="Distribución por grupos de edad (GRUPO_EDAD1)"),
        dcc.Graph(figure=fig_hist)
    ]),
    html.Div(style={"height":"24px"})
])

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
