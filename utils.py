
import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

NOFETAL_PATH = DATA_DIR / "Anexo1.NoFetal2019_CE_15-03-23.xlsx"
CODIGOS_PATH = DATA_DIR / "Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx"
DIVIPOLA_PATH = DATA_DIR / "Divipola_CE_.xlsx"

def load_nofetal():
    df = pd.read_excel(NOFETAL_PATH)
    df.columns = [c.upper() for c in df.columns]
    expected = ['COD_DANE','COD_DEPARTAMENTO','COD_MUNICIPIO','AÑO','MES','SEXO','GRUPO_EDAD1','COD_MUERTE']
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en NoFetal: {missing}")
    for col in ['COD_DEPARTAMENTO','COD_MUNICIPIO','MES','SEXO','GRUPO_EDAD1']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce').fillna(2019).astype(int)
    df['COD_MUERTE'] = df['COD_MUERTE'].astype(str).str.strip().str.upper()
    df['ICD4'] = df['COD_MUERTE'].str[:4]
    return df

def load_codigos():
    df = pd.read_excel(CODIGOS_PATH, sheet_name='Final', header=8)
    df.columns = [str(c).strip().upper() for c in df.columns]
    code_col_candidates = [c for c in df.columns if "CIE-10" in c or "CIE10" in c or "CÓDIGO" in c or "CODIGO" in c]
    desc_col_candidates = [c for c in df.columns if "DESCRIP" in c]
    if not code_col_candidates or not desc_col_candidates:
        df = pd.read_excel(CODIGOS_PATH, sheet_name='Final', header=None, skiprows=8)
        df = df.iloc[:, :2]
        df.columns = ['CODIGO','DESCRIPCION']
        code_col = 'CODIGO'; desc_col='DESCRIPCION'
    else:
        code_col = code_col_candidates[0]
        desc_col = desc_col_candidates[0]
        df = df[[code_col, desc_col]].rename(columns={code_col:'CODIGO', desc_col:'DESCRIPCION'})
    df['CODIGO'] = df['CODIGO'].astype(str).str.strip().str.upper()
    df['ICD4'] = df['CODIGO'].str[:4]
    df = df.dropna(subset=['ICD4'])
    df = df.drop_duplicates(subset=['ICD4'])
    return df[['ICD4','DESCRIPCION']]

def load_divipola():
    df = pd.read_excel(DIVIPOLA_PATH)
    df.columns = [c.upper() for c in df.columns]
    expected = ['COD_DANE','COD_DEPARTAMENTO','DEPARTAMENTO','COD_MUNICIPIO','MUNICIPIO']
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en Divipola: {missing}")
    for c in ['COD_DEPARTAMENTO','COD_MUNICIPIO']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['DEPTO_STR'] = df['COD_DEPARTAMENTO'].astype(int).astype(str).str.zfill(2)
    df['MPIO_STR']  = df['COD_MUNICIPIO'].astype(int).astype(str).str.zfill(3)
    df['DANE_MPIO'] = df['DEPTO_STR'] + df['MPIO_STR']
    return df

DEPT_CENTROIDS = {
    5:  (6.2442, -75.5812),
    8:  (10.9639, -74.7964),
    11: (4.7110, -74.0721),
    13: (10.3997, -75.5144),
    15: (5.4545, -73.3620),
    17: (5.0689, -75.5174),
    18: (1.6136, -75.6121),
    19: (2.4448, -76.6147),
    20: (10.4631, -73.2532),
    23: (8.7607, -75.8771),
    25: (4.4389, -74.6943),
    27: (5.6947, -76.6612),
    41: (2.9386, -75.2819),
    44: (11.5449, -72.9070),
    47: (11.2408, -74.1990),
    50: (4.1377, -73.6291),
    52: (1.2136, -77.2811),
    54: (7.9075, -72.5043),
    63: (4.5339, -75.6811),
    66: (4.8143, -75.6946),
    68: (7.1254, -73.1198),
    70: (9.3047, -75.3978),
    73: (4.4389, -75.2322),
    76: (3.4516, -76.5320),
    81: (6.9510, -71.8570),
    85: (5.3489, -72.4094),
    86: (1.1520, -76.6500),
    88: (12.5830, -81.7006),
    91: ( -4.2153, -69.9406),
    94: (2.5729, -67.4891),
    95: (2.5729, -72.6459),
    97: (1.1990, -70.1735),
    99: (5.4141, -69.7146),
}

AGE_GROUPS = {
    "Neonatal (<1 mes)": list(range(0,5)),
    "Infantil (1–11m)": [5,6],
    "1–4 años": [7,8],
    "5–14 años": [9,10],
    "15–19 años": [11],
    "20–29 años": [12,13],
    "30–44 años": [14,15,16],
    "45–59 años": [17,18,19],
    "60–84 años": [20,21,22,23,24],
    "85+ años": [25,26,27,28],
    "Edad desconocida": [29],
}

def map_age_group(code):
    try:
        code = int(code)
    except Exception:
        return "Edad desconocida"
    for label, codes in AGE_GROUPS.items():
        if code in codes:
            return label
    return "Edad desconocida"

def preprocess():
    df = load_nofetal()
    cod = load_codigos()
    divi = load_divipola()
    df = df.merge(divi[['COD_DEPARTAMENTO','COD_MUNICIPIO','DEPARTAMENTO','MUNICIPIO']], 
                  on=['COD_DEPARTAMENTO','COD_MUNICIPIO'], how='left')
    df = df.merge(cod, on='ICD4', how='left')
    df = df.rename(columns={'DESCRIPCION': 'CAUSA_NOMBRE'})
    df['GRUPO_EDAD_LABEL'] = df['GRUPO_EDAD1'].apply(map_age_group)
    return df
