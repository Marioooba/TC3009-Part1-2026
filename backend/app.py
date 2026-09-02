"""API del tablero de precios de vivienda.

Sesion 1: sirve agregados y registros del dataset. Todavia no hay modelo.
El contrato que implementa este archivo esta en docs/api-contrato.md.
"""

import os
import re

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

API_VERSION = "1.0.0"

# Las diez features que va a consumir el modelo en la sesion 2, mas Id y el target.
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

DATA_PATH = os.environ.get(
    "DATA_PATH",
    os.path.join(os.path.dirname(__file__), "..", "data", "train.csv"),
)

app = Flask(__name__)

# CORS solo para desarrollo.
#
# El frontend corre en el puerto 3000 y el backend en el 8080: puertos distintos
# son origenes distintos, y el navegador bloquea la peticion si el servidor no
# autoriza explicitamente a quien la hace.
#
# Se autoriza por PATRON y no por direccion literal, porque la IP publica de la
# instancia cambia cada vez que el laboratorio la reinicia. El patron sigue
# rechazando cualquier otro origen: no es "permitir todo".
#
# En produccion esto desaparece: un solo contenedor sirve el frontend construido
# y la API desde el mismo origen, y entonces no hay dos origenes que reconciliar.
# TODO sesion 1: escribe aqui las dos lineas que autorizan al tablero.
#                Sin ellas el tablero no va a poder pedir datos.
ORIGEN_DESARROLLO = re.compile(r"^http://[A-Za-z0-9.\-]+:3000$")
CORS(app, origins=[ORIGEN_DESARROLLO])
# ATAJO-P1: el CSV se carga completo en memoria al arrancar y nunca se recarga.
#           Alcanza para 1460 filas y hace la sesion 1 legible.
#           Parte 2 -> base de datos, consultas, paginacion real.
df = pd.read_csv(DATA_PATH)


@app.get("/api/health")
def health():
    """Estado del servicio.

    En la sesion 2 esta respuesta crece con model_version, sklearn_version y
    artifact_hash, cuando exista un artefacto del que informar.
    """
    return jsonify({"status": "ok", "api_version": API_VERSION})


# api stats
@app.get("/api/stats")
def stats():
    """Agregados del dataset. Alimenta las graficas del tablero.

    Si llega el parametro neighborhood, las estadisticas del target y el desglose
    por calidad se calculan solo sobre esa colonia. El desglose por colonia se
    mantiene global a proposito: es el eje de comparacion, y filtrarlo a una sola
    colonia lo dejaria sin sentido.
    """
    neighborhood = request.args.get("neighborhood")
    alcance = df[df["Neighborhood"] == neighborhood] if neighborhood else df

    # Siempre sobre df completo, nunca sobre el alcance filtrado.
    por_colonia = (
        df.groupby("Neighborhood")[TARGET_COLUMN]
        .agg(["count", "mean"])
        .reset_index()
        .sort_values("mean", ascending=False)
    )
    by_neighborhood = [
        {
            "neighborhood": fila["Neighborhood"],
            "count": int(fila["count"]),
            "mean_price": round(float(fila["mean"]), 1),
        }
        for _, fila in por_colonia.iterrows()
    ]

    # Una colonia sin registros no es un error: es un resultado vacio.
    if len(alcance) == 0:
        return jsonify(
            {
                "count": 0,
                "scope": neighborhood,
                "target": None,
                "by_neighborhood": by_neighborhood,
                "by_overall_qual": [],
            }
        )

    precios = alcance[TARGET_COLUMN]
    por_calidad = (
        alcance.groupby("OverallQual")[TARGET_COLUMN]
        .agg(["count", "mean"])
        .reset_index()
        .sort_values("OverallQual")
    )

    # Los tipos de numpy no son serializables a JSON: int() y float() no son
    # adorno. Sin ellos el servidor truena con
    # "Object of type int64 is not JSON serializable".
    return jsonify(
        {
            "count": int(len(alcance)),
            "scope": neighborhood,
            "target": {
                "name": TARGET_COLUMN,
                "min": int(precios.min()),
                "mean": round(float(precios.mean()), 1),
                "median": int(precios.median()),
                "max": int(precios.max()),
            },
            "by_neighborhood": by_neighborhood,
            "by_overall_qual": [
                {
                    "overall_qual": int(fila["OverallQual"]),
                    "count": int(fila["count"]),
                    "mean_price": round(float(fila["mean"]), 1),
                }
                for _, fila in por_calidad.iterrows()
            ],
        }
    )


# api data
@app.get("/api/data")
def data():
    """Registros individuales, con filtro opcional por colonia."""
    neighborhood = request.args.get("neighborhood")

    try:
        limit = int(request.args.get("limit", DEFAULT_LIMIT))
    except ValueError:
        limit = DEFAULT_LIMIT
    limit = max(1, min(limit, MAX_LIMIT))

    filtrado = df
    if neighborhood:
        filtrado = filtrado[filtrado["Neighborhood"] == neighborhood]

    # Un filtro sin coincidencias devuelve una lista vacia con 200, no un error.
    # Una busqueda vacia es un resultado legitimo; un error es que algo salio mal.
    total = int(len(filtrado))
    pagina = filtrado.head(limit)[EXPOSED_COLUMNS]

    return jsonify(
        {
            "count": int(len(pagina)),
            "total_matching": total,
            "rows": pagina.to_dict(orient="records"),
        }
    )


if __name__ == "__main__":
    # host="0.0.0.0" escucha en todas las interfaces. Sin esto, la API solo
    # respondaria a la propia instancia y tu navegador veria un timeout.
    #
    # El puerto 8080 tiene que estar abierto en el security group de la
    # instancia; si no, el paquete ni siquiera llega.
    app.run(host="0.0.0.0", port=8080, debug=True)
