"""Sesion 1: los datos del tablero.

Sirve agregados y registros del dataset. Todavia no hay modelo.
El contrato que implementa este archivo esta en docs/api-contrato.md.
"""

import os
import pathlib

import pandas as pd
from flask import Blueprint, jsonify, request

bp = Blueprint("s1_tablero", __name__)

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# Las diez features que consume el modelo desde la sesion 2, mas Id y el target.
# El tablero y el predictor hablan del mismo vocabulario desde el dia uno.
FEATURE_COLUMNS = [
    "GrLivArea",
    "OverallQual",
    "YearBuilt",
    "TotalBsmtSF",
    "GarageCars",
    "FullBath",
    "BedroomAbvGr",
    "Neighborhood",
    "LotArea",
    "KitchenQual",
]
TARGET_COLUMN = "SalePrice"
EXPOSED_COLUMNS = ["Id"] + FEATURE_COLUMNS + [TARGET_COLUMN]

DEFAULT_LIMIT = 20
MAX_LIMIT = 200

DATA_PATH = os.environ.get("DATA_PATH", str(RAIZ / "data" / "train.csv"))

# ATAJO-P1: el CSV se carga completo en memoria al arrancar y nunca se recarga.
#           Alcanza para 1460 filas y hace la sesion 1 legible.
#           Parte 2 -> base de datos, consultas, paginacion real.
df = pd.read_csv(DATA_PATH)


# ---------------------------------------------------------------------------
# ESTADO DE ARRANQUE: los dos endpoints estan por escribir.
#
# app.py ya descubre este modulo y registra su blueprint, y /api/health ya
# responde. Lo que falta son los dos endpoints que alimentan el tablero.
# ---------------------------------------------------------------------------


# TODO sesion 1: GET /api/stats
#
# Devuelve los agregados del dataset. Alimenta las graficas del tablero.
# El contrato exacto esta en docs/api-contrato.md.
#
# Acepta un parametro opcional neighborhood que acota count, target y
# by_overall_qual. by_neighborhood se queda global a proposito: es el eje de
# comparacion, y filtrarlo a una sola colonia lo dejaria sin sentido.


# TODO sesion 1: GET /api/data
#
# Devuelve registros individuales, con filtro opcional por colonia y un limite.
# Un filtro sin coincidencias NO es un error: responde 200 con lista vacia.
