"""Comprueba las tres promesas del registro de predicciones (sesion 4).

    ./setup/run test

Son invariantes que se rompen en silencio: nada falla, nada avisa, y el dia
que alguien audite el historial los numeros no cuadran.

  1. Cada prediccion exitosa deja EXACTAMENTE una fila.
  2. Una peticion rechazada con 400 NO deja fila.
  3. El historial viene de mas reciente a mas antiguo.

La 1 y la 2 juntas son las que hacen que el log se pueda contar. Si un 400
dejara fila, cualquier metrica de uso estaria inflada; si una prediccion
dejara dos, tambien.

Corre contra una base de datos temporal: no toca la del alumno.
"""

import collections
import json
import os
import pathlib
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
VERDE, ROJO, RESET = "\033[32m", "\033[31m", "\033[0m"

fallos = []


def ok(m):
    print(f"  {VERDE}OK{RESET}    {m}")


def falla(m):
    print(f"  {ROJO}FALLA{RESET} {m}")
    fallos.append(m)


def main():
    print("\nRegistro de predicciones")
    print("=" * 54)

    ejemplo = RAIZ / "artifacts" / "example.json"
    if not ejemplo.exists():
        print("  no hay artefacto todavia; corre el notebook de la sesion 2.")
        return 0

    # Base de datos temporal: el modulo lee DB_PATH al importarse, asi que se
    # define ANTES del import.
    tmp = tempfile.mkdtemp()
    os.environ["DB_PATH"] = str(pathlib.Path(tmp) / "prueba.sqlite")
    sys.path.insert(0, str(RAIZ / "backend"))

    import app  # noqa: E402

    if not any(m.__name__ == "s4_producto" for m in app.modulos):
        print("  el modulo de la sesion 4 no esta escrito todavia; se omite.")
        return 0

    cliente = app.app.test_client()
    base = json.loads(ejemplo.read_text())["input"]

    # --- 12 predicciones validas, todas distintas ---
    ids = []
    for i in range(12):
        casa = dict(base, GrLivArea=1000 + i * 37)
        r = cliente.post("/api/predict", json=casa)
        if r.status_code != 200:
            falla(f"una prediccion valida devolvio {r.status_code}")
            return 1
        ids.append(r.get_json()["prediction_id"])

    # --- 5 peticiones invalidas ---
    for _ in range(5):
        r = cliente.post("/api/predict", json=dict(base, Neighborhood="Polanco"))
        if r.status_code != 400:
            falla(f"una categoria invalida devolvio {r.status_code}, esperado 400")

    filas = cliente.get("/api/history?limit=500").get_json()["rows"]
    en_log = [f["prediction_id"] for f in filas]

    print(f"\n  12 validas + 5 rechazadas  ->  {len(filas)} filas en el log\n")

    if len(filas) == 12:
        ok("cada prediccion exitosa dejo exactamente una fila")
    else:
        falla(f"hay {len(filas)} filas y deberia haber 12")

    repetidos = [k for k, v in collections.Counter(en_log).items() if v > 1]
    if repetidos:
        falla(f"hay prediction_id repetidos en el log: {repetidos[:3]}")
    elif set(ids) == set(en_log):
        ok("cada prediction_id devuelto corresponde a una fila, y solo una")
    else:
        falla("los ids del log no coinciden con los que devolvio /api/predict")

    if len(filas) == 12:
        ok("ninguna peticion rechazada con 400 genero fila")

    fechas = [f["created_at"] for f in filas]
    if fechas == sorted(fechas, reverse=True):
        ok("el historial viene de mas reciente a mas antiguo")
    else:
        falla("el historial no esta ordenado por fecha descendente")

    # El input completo, no solo el resultado: es lo que permite detectar
    # drift mas adelante.
    if filas and set(filas[0]["input"]) == set(base):
        ok(f"cada fila guarda el input completo ({len(base)} campos)")
    else:
        falla("las filas no guardan todas las features del input")

    # El limite se acota: el cliente nunca puede pedir "todo".
    acotado = cliente.get("/api/history?limit=99999").get_json()
    if acotado["count"] <= 500:
        ok("un limite absurdo se acota en lugar de fallar")
    else:
        falla("/api/history no acota el limite")

    print()
    if fallos:
        print(f"{ROJO}{len(fallos)} FALLAS.{RESET} El registro no se puede auditar.")
        return 1
    print(f"{VERDE}El registro cumple sus tres promesas.{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
