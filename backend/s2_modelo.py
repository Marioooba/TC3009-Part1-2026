"""Sesion 2: el modelo cruza la frontera.

Aqui vive TODO lo que el servicio necesita saber del modelo: cargar el
artefacto, verificar que sea compatible, validar la entrada contra el contrato,
y predecir.

Fijate en lo que este archivo NO hace: no imputa, no escala, no codifica, y no
invierte el logaritmo del target. Todo eso viaja dentro de pipeline.joblib. Si
este archivo tuviera que saber algo de eso, la exportacion estaria mal hecha.
"""

import json
import os
import pathlib
import uuid

import joblib
import pandas as pd
import sklearn
from flask import Blueprint, current_app, jsonify, request

bp = Blueprint("s2_modelo", __name__)

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# ATAJO-P1: el artefacto vive dentro del repositorio, junto al codigo.
#           Alcanza para un modelo de pocos megabytes y hace que desplegar
#           sea copiar una carpeta.
#           Parte 2 -> model registry con versionado y rollback.
#
# La ruta se lee de una variable de entorno y no esta escrita a mano: asi,
# cuando el artefacto se mueva a S3 en la Parte 2, no hay que tocar esta
# logica de carga.
MODEL_DIR = pathlib.Path(os.environ.get("MODEL_PATH", str(RAIZ / "artifacts")))


def cargar_artefacto():
    """Carga el pipeline y su contrato, y verifica que sean compatibles.

    La verificacion de version no es paranoia: joblib no es un formato estable.
    Un artefacto exportado con una version de scikit-learn y cargado con otra
    puede fallar al deserializar o --peor-- cargar y devolver numeros distintos
    sin avisar de nada.
    """
    ruta_contrato = MODEL_DIR / "metadata.json"
    ruta_pipeline = MODEL_DIR / "pipeline.joblib"

    if not ruta_contrato.exists() or not ruta_pipeline.exists():
        raise FileNotFoundError(
            f"no encuentro el artefacto en {MODEL_DIR}.\n"
            "    Corre el notebook notebooks/01-entrenar-y-exportar.ipynb "
            "para generarlo."
        )

    contrato = json.loads(ruta_contrato.read_text())
    pipeline = joblib.load(ruta_pipeline)

    entrenado_con = contrato["sklearn_version"]
    if entrenado_con != sklearn.__version__:
        print(
            "\n*** AVISO DE COMPATIBILIDAD ***\n"
            f"    El artefacto se entreno con scikit-learn {entrenado_con}\n"
            f"    y este servicio tiene instalada la {sklearn.__version__}.\n"
            "    Las predicciones pueden ser incorrectas sin dar ningun error.\n"
            "    Revisa backend/requirements.txt.\n",
            flush=True,
        )
    else:
        print(
            f"artefacto {contrato['model_version']} cargado "
            f"(scikit-learn {entrenado_con})",
            flush=True,
        )

    return pipeline, contrato


pipeline, contrato = cargar_artefacto()


def estado():
    """Lo que este modulo aporta a /api/health.

    Que el estado del servicio diga QUE modelo esta sirviendo no es un detalle:
    es lo que permite saber, mirando una URL, si un despliegue quedo con el
    artefacto que esperabas. En la Parte 2 es lo que hace posible un rollback.
    """
    return {
        "model_version": contrato["model_version"],
        "sklearn_version": sklearn.__version__,
        "artifact_hash": contrato["artifact_hash"],
    }


class InputInvalido(Exception):
    """El cliente mando algo que el contrato no acepta."""


def validar(payload):
    """Valida la entrada CONTRA EL CONTRATO, no contra reglas escritas a mano.

    Esto es lo que hace que el servicio siga siendo correcto cuando el modelo
    cambia: si el contrato gana una feature, la validacion la exige sola.

    Devuelve el DataFrame de una fila listo para el pipeline, y la lista de
    advertencias que no invalidan la peticion.
    """
    if not isinstance(payload, dict):
        raise InputInvalido("el cuerpo de la peticion debe ser un objeto JSON")

    fila = {}
    advertencias = []

    for f in contrato["features"]:
        nombre = f["name"]
        if nombre not in payload:
            raise InputInvalido(f"falta la feature '{nombre}'")
        valor = payload[nombre]

        if f["type"] == "num":
            try:
                valor = float(valor)
            except (TypeError, ValueError):
                raise InputInvalido(f"'{nombre}' debe ser un numero, llego {valor!r}")
            # Fuera de rango NO es un error: es una casa legitima que el modelo
            # no vio al entrenar. Rechazarla seria un mal producto; predecir sin
            # avisar seria deshonesto. Se predice Y se avisa.
            if valor < f["min"] or valor > f["max"]:
                advertencias.append(
                    f"'{nombre}' = {valor:g} esta fuera del rango visto al "
                    f"entrenar ({f['min']:g} a {f['max']:g}); la prediccion es "
                    "menos confiable"
                )
        else:
            if valor not in f["allowed"]:
                raise InputInvalido(
                    f"'{nombre}' no acepta el valor {valor!r}. "
                    f"Valores validos: {', '.join(map(str, f['allowed']))}"
                )

        fila[nombre] = valor

    return pd.DataFrame([fila]), advertencias


@bp.get("/api/model")
def model():
    """El contrato del modelo, tal cual. Alimenta el formulario y la Model Card.

    El frontend no tiene una lista de features escrita a mano: la pide aqui. Si
    el modelo cambia, el formulario cambia solo.
    """
    return jsonify(contrato)


@bp.post("/api/predict")
def predict():
    """Una casa entra, un precio sale."""
    try:
        entrada, advertencias = validar(request.get_json(silent=True))
    except InputInvalido as e:
        # 400: el cliente mando algo invalido, y se le dice QUE fue.
        return jsonify({"error": str(e)}), 400

    try:
        # El pipeline recibe el DataFrame CRUDO. Toda la transformacion --y la
        # inversion del logaritmo del target-- viaja dentro del artefacto.
        precio = float(pipeline.predict(entrada)[0])
    except Exception:
        # 500: fallamos nosotros. El detalle va a los registros del servidor, no
        # a la respuesta: al cliente no se le entrega el interior de la casa.
        current_app.logger.exception("fallo la prediccion")
        return jsonify({"error": "no se pudo generar la prediccion"}), 500

    return jsonify(
        {
            # ATAJO-P1: el prediction_id se genera y se devuelve, pero todavia
            #           no se guarda en ningun lado.
            #           Sesion 3 -> log en SQLite. Parte 2 -> monitoreo y drift.
            "prediction_id": str(uuid.uuid4()),
            "prediction": round(precio, 2),
            "model_version": contrato["model_version"],
            "warnings": advertencias,
        }
    )
