"""El unico test que de verdad importa en este modulo.

Comprueba que el notebook y el servicio devuelven EL MISMO NUMERO para el
mismo input.

    notebook                              servicio
    ────────────────────                  ─────────────────────────
    pipeline.predict(ejemplo)             POST /api/predict (example.json)
             │                                      │
             ▼                                      ▼
        141,334.96                            141,334.96
             └──────────── ¿iguales? ───────────────┘

Si no coinciden, la costura entre el modelo y el producto esta rota, y las
causas posibles son siempre las mismas:

  · el servicio transforma la entrada por su cuenta en lugar de dejar que lo
    haga el pipeline
  · se reemplazo pipeline.joblib sin regenerar example.json
  · la version de scikit-learn del servicio no es la del entrenamiento
  · la inversion del target quedo fuera del artefacto

Se corre desde la raiz del proyecto:

    .venv/bin/python tests/test_paridad.py
"""

import importlib.util
import json
import os
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TOLERANCIA = 0.01  # centavos: es el mismo modelo, no una aproximacion

fallos = 0


def ok(mensaje):
    print(f"  OK    {mensaje}")


def falla(mensaje):
    global fallos
    fallos += 1
    print(f"  FALLA {mensaje}")


def cargar_servicio():
    os.environ.setdefault("DATA_PATH", str(RAIZ / "data" / "train.csv"))
    os.environ.setdefault("MODEL_PATH", str(RAIZ / "artifacts"))
    sys.path.insert(0, str(RAIZ / "backend"))
    spec = importlib.util.spec_from_file_location("app", RAIZ / "backend" / "app.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def main():
    ruta_ejemplo = RAIZ / "artifacts" / "example.json"
    if not ruta_ejemplo.exists():
        print("\nNo existe artifacts/example.json.")
        print("Corre el notebook notebooks/01-entrenar-y-exportar.ipynb primero.\n")
        return 1

    ejemplo = json.loads(ruta_ejemplo.read_text())
    esperado = ejemplo["prediction"]

    print()
    print("Paridad notebook <-> servicio")
    print("=" * 54)

    modulo = cargar_servicio()
    cliente = modulo.app.test_client()

    respuesta = cliente.post("/api/predict", json=ejemplo["input"])
    if respuesta.status_code != 200:
        print(f"\n  El servicio respondio {respuesta.status_code}:")
        print(f"  {respuesta.get_json()}\n")
        return 1

    cuerpo = respuesta.get_json()
    obtenido = cuerpo["prediction"]
    diferencia = abs(obtenido - esperado)

    print()
    print(f"  notebook   {esperado:>16,.2f}")
    print(f"  servicio   {obtenido:>16,.2f}")
    print(f"  diferencia {diferencia:>16,.2f}")
    print()

    if diferencia <= TOLERANCIA:
        ok("las predicciones coinciden")
    else:
        falla(f"difieren en mas de {TOLERANCIA}: la costura esta rota")

    # La version del modelo tiene que viajar con la prediccion.
    if cuerpo["model_version"] == ejemplo["model_version"]:
        ok(f"la version del modelo coincide ({cuerpo['model_version']})")
    else:
        falla(
            f"el servicio sirve {cuerpo['model_version']} y el ejemplo se genero "
            f"con {ejemplo['model_version']}: no es el mismo artefacto"
        )

    # La version de scikit-learn del contrato tiene que ser la instalada.
    import sklearn

    s2 = sys.modules.get("s2_modelo")
    entrenado_con = s2.contrato["sklearn_version"]
    if entrenado_con == sklearn.__version__:
        ok(f"scikit-learn coincide ({entrenado_con})")
    else:
        falla(
            f"entrenado con scikit-learn {entrenado_con}, "
            f"sirviendo con {sklearn.__version__}"
        )

    # El servicio NO debe invertir el target: eso viaja en el artefacto.
    fuente = (RAIZ / "backend" / "s2_modelo.py").read_text()
    if "expm1" in fuente:
        falla(
            "el servicio menciona expm1: la inversion del target deberia vivir "
            "dentro del pipeline, no aqui"
        )
    else:
        ok("el servicio no invierte el target por su cuenta")

    # El artefacto no debe arrastrar rutas absolutas del entorno de entrenamiento.
    crudo = (RAIZ / "artifacts" / "pipeline.joblib").read_bytes()
    for basura in (b"/Users/", b"/home/", b"C:\\\\"):
        if basura in crudo:
            falla(f"el artefacto contiene rutas absolutas ({basura.decode()})")
            break
    else:
        ok("el artefacto no contiene rutas absolutas")

    print()
    if fallos:
        print(f"{fallos} FALLAS: la costura esta rota.")
        return 1
    print("La costura esta sana.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
