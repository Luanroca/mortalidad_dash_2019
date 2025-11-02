
# Dashboard de Mortalidad en Colombia (2019) — Dash + Plotly

Autor: Luis Andres Rodriguez Carrillo  
Fuente de datos: DANE — Estadísticas Vitales (EEVV) 2019 (No fetal).

## Introducción
Esta aplicación web interactiva permite explorar la mortalidad en Colombia para el año 2019 utilizando los microdatos de defunciones no fetales. Provee visualizaciones que facilitan la interpretación de patrones demográficos y regionales de mortalidad.

## Objetivo
Construir un dashboard interactivo que integre:
- Mapa (centroides departamentales) con la distribución total de muertes.
- Serie temporal del total mensual de muertes.
- Top 5 ciudades con más homicidios (ICD-10 X95).
- 10 ciudades con menor mortalidad (total defunciones).
- Tabla de 10 principales causas de muerte (código y nombre).
- Barras apiladas por sexo y departamento.
- Distribución por grupos de edad (GRUPO_EDAD1) según categorías DANE.

## Estructura del proyecto
mortality_dash_2019/
 ├── app.py
 ├── utils.py
 ├── requirements.txt
 ├── Procfile
 ├── assets/
 │   └── style.css
 └── data/
     ├── Anexo1.NoFetal2019_CE_15-03-23.xlsx
     ├── Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx
     └── Divipola_CE_.xlsx

## Requisitos
- Python 3.10+
- Librerías:
  - dash==2.17.1
  - plotly==5.24.1
  - pandas==2.2.2
  - numpy==1.26.4
  - openpyxl==3.1.5
  - gunicorn==22.0.0

Instalación de requisitos:
  pip install -r requirements.txt


## Ejecución local
  python app.py
  (Abre en http://127.0.0.1:8050)

## Despliegue (Render)
1. Crea un repositorio en GitHub con esta estructura.
2. En Render, crea un Web Service nuevo desde GitHub.
   - Runtime: Python 3.10+
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:server
3. Sube los archivos de datos a la carpeta data/ en tu repo (o usa almacenamiento remoto).
4. Una vez Live, comparte la URL pública.

### Despliegue (Railway)
- Conecta el repo y define Start Command como: gunicorn app:server

### Despliegue (Google App Engine)
- Agrega un archivo app.yaml con:
    runtime: python310
    entrypoint: gunicorn -b :$PORT app:server
- Despliega con: gcloud app deploy

### Despliegue (AWS Elastic Beanstalk)
- Empaqueta el repo y crea una aplicación Python.
- Comando de inicio: gunicorn app:server

## Visualizaciones y hallazgos
- Mapa (centroides): tamaño de burbuja indica el total de muertes por departamento.
- Serie por mes: variaciones estacionales en 2019.
- Top 5 homicidios (X95): ranking municipal para agresión con arma de fuego.
- Bottom 10 mortalidad: municipios con menor conteo total.
- Top 10 causas: tabla con códigos ICD-10 (4 caracteres) y sus descripciones.
- Barras apiladas por sexo: comparación Hombres vs. Mujeres por departamento.
- Grupos de edad (GRUPO_EDAD1): categorías mapeadas según lineamientos DANE.

Nota: El archivo de códigos CIE-10 incluye metadatos previos. En utils.py se normaliza a partir de la fila 9 (header=8).

## Software
Python, Dash, Plotly, Pandas, Numpy, OpenPyXL, Gunicorn.

## Instalación
  git clone <URL-DE-TU-REPO>.git
  cd mortality_dash_2019
  pip install -r requirements.txt
  python app.py

## Enlaces de interés
- Catálogo del DANE (EEVV 2019): https://microdatos.dane.gov.co/index.php/catalog/696
