# Sesión 2 — La costura

**Dos horas.** Al final, tu tablero va a poder predecir el precio de una casa que nadie ha
visto — y vas a saber por qué eso es más difícil de lo que parece.

Esta es la sesión más importante del módulo. Lo que aprendas hoy es lo que vas a usar en tu
reto, y es lo que separa un notebook que predice bien de un producto que sirve.

```
   0:00  qué cruza la frontera                          8 min
   0:08  traer el material de la sesión                 7 min
   0:15  correr el notebook en Colab                   20 min
   0:35  la exportación, a fondo                       25 min
   1:00  el servicio: cargar, validar, predecir        40 min
   1:40  el test que importa                           12 min
   1:52  cierre                                         8 min
```

---

## Antes de empezar: ¿no estuviste en la sesión 1?

No pasa nada, y no tienes que ponerte al día tecleando. Hay un atajo previsto — **pero
necesitas tu instancia ya creada y aprovisionada.**

### Si ya tienes tu instancia funcionando

**En tu computadora:**

```bash
./setup/run recuperar 1 --si
git push --force
```

**Y en la instancia:**

```bash
./setup/run sync
./setup/run start
```

La instancia clonó por HTTPS y no tiene credenciales de GitHub: **solo puede hacer `pull`**.
Por eso `recuperar` va en tu computadora — si lo corres allá, tu fork se queda atrás y el
siguiente `push` te devuelve al estado viejo.

Eso te deja con **la sesión 1 completa** —el tablero funcionando— y con el esqueleto de la
sesión 2 listo para llenar. No tienes que reinstalar nada: las dependencias del modelo
(`scikit-learn`, `joblib`) se fijaron desde la sesión 1 justo para esto.

Abre `http://TU-IP:3000` y comprueba que ves el tablero con datos. Si lo ves, estás al día y
puedes seguir esta guía desde el principio.

⚠ `git reset --hard` **descarta** lo que llevaras avanzado de la sesión 1. Si escribiste algo
que quieras conservar, cópialo aparte antes.

### Si no tienes instancia todavía

Eso sí no cabe en esta sesión: crear y aprovisionar la instancia toma unos 45 minutos.
Avísale al profesor al llegar. Mientras, siéntate con un compañero y sigue la sesión en su
máquina — lo importante de hoy se entiende viendo, y tu instancia la montas después con
[docs/s1-guia.md](s1-guia.md).

---

## 0:00 — Qué cruza la frontera (8 min)

La sesión pasada montaste un tablero que lee un CSV. Hoy entra el modelo. Y el modelo no es
un archivo que se copia: es un objeto que hay que **exportar bien**.

```
      TU NOTEBOOK                              TU SERVICIO
   ┌────────────────┐                      ┌────────────────┐
   │  X = df[...]   │                      │  llega JSON    │
   │  imputar       │   ¿qué cruza?        │  con 10 campos │
   │  escalar       │  ═══════════════▶    │       ↓        │
   │  one-hot       │                      │  ¿y ahora?     │
   │  log(y)        │                      │                │
   │  fit           │                      │                │
   └────────────────┘                      └────────────────┘
```

El error que comete casi todo el mundo la primera vez: exportar **sólo el estimador**. Llega
un JSON con 10 campos, y el modelo espera una matriz de 250 columnas escaladas y codificadas.
Nadie sabe reconstruirla, y el proyecto se muere ahí.

La respuesta es una sola idea, y es la que se llevan hoy:

> **Lo que se serializa no es el modelo: es el pipeline completo.**

---

## 0:08 — Traer el material de la sesión (7 min)

El curso publicó los archivos de esta sesión. Tráelos **sin pisar tu código**:

**En tu computadora:**

```bash
./setup/run actualizar 2
```

> **Dónde se corre esto.** En tu computadora, no en la instancia. `actualizar` trae archivos
> **con `TODO` por llenar**, y esos los editas en VS Code. Si los traes a la instancia, ahí es
> donde quedan — y la instancia no puede hacer `push`, así que tu repositorio nunca los ve.
>
> ```
>    Tu computadora  ─push──▶  tu fork  ─pull──▶  Tu instancia
>       editas                              solo ejecuta
> ```
>
> La regla, la misma de la sesión 1: **si cambia archivos, va en tu computadora.**

> **Si eso falla porque hiciste fork antes de que existiera esta sesión**, tu copia de los
> comandos es la vieja. Actualízala primero y vuelve a intentar:
>
> ```bash
> git remote add curso https://github.com/vsosahdz/TC3009-Part1-2026.git
> git fetch --force --tags curso
> git checkout curso/main -- setup/
> ./setup/run actualizar 2
> ```
>
> Pasa una sola vez. De aquí en adelante `actualizar` lee del curso directamente y no
> depende de lo que tenga tu fork.

Eso trae las guías, el notebook y los esqueletos nuevos, y **conserva intacto lo que
escribiste** en la sesión 1. El reparto de quién es dueño de qué archivo está en
`setup/archivos-del-curso.txt`, para que lo puedas revisar.

Fíjate en lo que **no** pasó: no hubo conflictos. Eso es a propósito — cada sesión vive en
archivos propios:

```
   backend/
   ├── app.py           el ensamblador. no lo editas nunca
   ├── s1_tablero.py    lo que escribiste la sesión pasada
   └── s2_modelo.py     ← lo de hoy, archivo nuevo
```

`app.py` descubre los módulos solos y los registra. Por eso agregar una sesión nunca toca el
código de la anterior.

Guarda y súbelo, **desde tu computadora**:

```bash
git add -A && git commit -m "material de la sesion 2"
git push
```

Y en **la instancia**, tráelo e instala lo que haga falta:

```bash
./setup/run sync
bash setup/bootstrap-ec2.sh
```

---

## 0:15 — Corre el notebook en Colab (20 min)

El notebook corre en **Google Colab**, no en tu computadora ni en la instancia.

¿Por qué ahí? Porque tu laptop no tiene Python —nunca lo instalaste, a propósito— y la
instancia no tiene interfaz gráfica. Colab te da un entorno con todo listo y sin instalar
nada.

### Ábrelo en Colab

1. Ve a [colab.research.google.com](https://colab.research.google.com)
2. **Archivo → Subir cuaderno**, y sube `notebooks/01-entrenar-y-exportar.ipynb` de tu
   proyecto
3. En el panel de la izquierda (el icono de carpeta 📁), **arrastra tu carpeta `data`
   completa**

Te tiene que quedar así:

```
   /content/
   └── data/
       └── train.csv
```

> ⚠ Lo que subas a Colab **se borra al cerrar la sesión**. Por eso al final del notebook vas
> a descargar el artefacto: no se queda ahí.

Ahora córrelo de arriba a abajo.

### La primera celda no es relleno

Instala las versiones exactas de `numpy`, `pandas`, `scikit-learn` y `joblib` que están en
`backend/requirements.txt`. Colab trae las suyas, y **no son necesariamente las de tu
servidor**.

Si la celda de verificación te pide reiniciar el entorno, hazlo: *Entorno de ejecución →
Reiniciar sesión*, y vuelve a correr desde ahí. Colab necesita reiniciar cuando cambia una
librería que ya tenía cargada.

Esto va a parecer un trámite hasta la sesión donde alguien lo salte y su modelo devuelva
números distintos en el servidor.

Ya llevaste un módulo entero de modelado: aquí no vamos a hablar de hiperparámetros. Lo único
que vale la pena mirar mientras corre son **dos decisiones**:

### Las diez features, y por qué no son las mejores

El dataset tiene 79 columnas. El formulario expone 10. Y no son las 10 que dan el mejor RMSE:
son **las 10 que un vendedor puede contestar sin medir la casa**.

```
   79 features
        │
        ├── 10 que el usuario SÍ conoce   ──▶  el formulario
        │
        └── las otras 69                  ──▶  fuera
```

La pregunta incómoda: ¿re-entrenamos con 10, o rellenamos las otras 69 con medianas para
tener mejor RMSE? Rellenar da mejores números y **es un producto que miente**: finge conocer
datos que no tiene. Re-entrenamos.

Ese trade-off —score contra honestidad— es una decisión de producto, no de modelado. Vas a
tomar la misma en tu reto.

### El artefacto pesa 9 MB, y eso también es una decisión

El bosque tiene 100 árboles y no 300. Con 300 el artefacto pesaría 27 MB y las métricas
serían las mismas.

Importa porque **ese archivo tiene que viajar**: lo vas a descargar de Colab, subirlo a tu
repositorio y traerlo a tu instancia. Tres veces por cada cambio. El tamaño del artefacto es
una decisión de producto, no un detalle de configuración.

### `OverallQual` pesa 0.58 de la importancia total

Es, con diferencia, la feature más influyente. Y es una **calificación subjetiva del 1 al
10**. O sea: la mayor parte de tu predicción depende de que alguien juzgue bien la calidad de
su propia casa.

No hay nada que arreglar ahí. Pero un producto honesto lo sabe, y en la sesión 3 lo vas a
mostrar en la interfaz.

---

## 0:35 — La exportación, a fondo (25 min)

Aquí está el contenido de la sesión. ### Bájalo de Colab y llévalo a tu repositorio

La última celda del notebook te descarga un `artifacts.zip`. Descomprímelo en tu proyecto, de
forma que quede en `artifacts/`, y súbelo:

**En tu computadora:**

```bash
git add artifacts/
git commit -m "artefacto de la sesion 2"
git push
```

**En la instancia:**

```bash
./setup/run sync
```

```
   Colab            tu computadora         GitHub          tu instancia
   ─────            ──────────────         ──────          ────────────
   entrena   ─zip─▶  artifacts/    ─push─▶   ...    ─sync─▶  lo usa el servicio
```

**Entrenaste en un lado y vas a servir en otro.** El artefacto viaja por git, igual que el
código. Es la misma lección de la sesión 1, aplicada a un archivo binario.

---

El notebook exporta **tres archivos**, no uno:

```
   artifacts/
   ├── pipeline.joblib     el Pipeline COMPLETO
   ├── metadata.json       el CONTRATO, en texto legible
   └── example.json        un input válido y su predicción de referencia
```

### 1 · `pipeline.joblib` — por qué el preprocesamiento va dentro

Mira la celda del pipeline en tu notebook. El `ColumnTransformer` **no está en una celda
aparte**: es parte del objeto que se serializa.

```
   ✗  joblib.dump(modelo)
      + "acuérdate de imputar, escalar y hacer one-hot antes de predecir"
      → el conocimiento vive en la cabeza de quien exportó

   ✓  joblib.dump(pipeline_completo)
      → pipeline.predict(df_crudo) simplemente funciona
```

### 2 · La transformación del target, también dentro

`TransformedTargetRegressor(regressor=..., func=np.log1p, inverse_func=np.expm1)`.

La alternativa sería aplicar `np.expm1()` en el código de Flask. Es peor, y no por estilo:

```
   ✗  precio = np.expm1(pipeline.predict(X))
      → el siguiente que consuma tu modelo lo va a olvidar
        y va a servir precios de 12.3 dólares

   ✓  pipeline.predict(X) YA devuelve pesos
      → el artefacto se autocontiene
```

En tu notebook hay un `assert` que lo comprueba antes de exportar. Si la predicción sale
entre 10 y 14, la transformación quedó fuera.

### 3 · `metadata.json` — un archivo, tres consumidores

```
                    ┌──▶ el servicio VALIDA la entrada contra él
   metadata.json ───┼──▶ la Model Card se RENDERIZA de él
                    └──▶ la rúbrica de tu reto se EVIDENCIA con él
```

Ábrelo y busca `sklearn_version`. Ese campo existe porque **`joblib` no es un formato
estable**: un artefacto exportado con una versión de scikit-learn y cargado con otra puede
fallar al deserializar, o —mucho peor— cargar y devolver números distintos sin avisar de nada.

Por eso `backend/requirements.txt` fija versiones exactas con `==`, y por eso el servicio va
a comparar esa versión al arrancar.

### 4 · Las importancias, traducidas

El modelo ve `Neighborhood_NAmes`, `Neighborhood_CollgCr`... y para el contrato queremos
`Neighborhood` completo. El notebook suma las columnas que salieron de cada feature original.

Eso se hace **en el notebook y no en el servicio**: el servicio no debería tener que hurgar
dentro de un pipeline anidado.

### 5 · Qué NO fue al artefacto

- **Los datos de entrenamiento.** El artefacto lleva el modelo, no el CSV.
- **Credenciales.** Nunca, en ningún artefacto.
- **Rutas absolutas de tu máquina.** El clásico: un pipeline que congela
  `/Users/tu-nombre/...` dentro del pickle y truena en el servidor. El test de hoy lo revisa.

---

## 1:00 — El servicio: cargar, validar, predecir (40 min)

**En tu computadora**, abre `backend/s2_modelo.py`. Está a medias, con cuatro `TODO`.

El archivo empieza así, y vale leer el comentario antes de escribir nada:

```python
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
```

### `TODO 1` — cargar el artefacto y verificar que sea compatible

```python
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
```

Dos cosas que acabas de resolver:

**La ruta sale de una variable de entorno.** No está escrita a mano, y eso no es paranoia: en
la Parte 2 el artefacto se va a mover a un model registry, y esta lógica de carga no va a
tener que cambiar.

**La verificación de versión avisa y no truena.** Un mismatch no impide arrancar —a veces
funciona— pero **sí imprime una advertencia imposible de ignorar**. El fallo silencioso es
peor que el ruidoso.

Y `estado()` es lo que hace que `/api/health` reporte qué modelo está sirviendo. Que puedas
saber eso mirando una URL es lo que en la Parte 2 hace posible un rollback.

### `TODO 2` — validar la entrada contra el contrato

```python
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
```

Lo importante de esta función es lo que **no** tiene: reglas escritas a mano. Todo sale de
`contrato["features"]`. Si el modelo gana una feature, la validación la exige sola.

Y una decisión de producto escondida en ese `if`:

```
   feature faltante        →  400. No podemos predecir sin ella.
   categoría inexistente   →  400. El modelo nunca la vio.
   número fuera de rango   →  200 + advertencia
```

¿Por qué fuera de rango **no** es un error? Porque una casa de 8,000 pies cuadrados es una
casa legítima. Rechazarla sería un mal producto. Predecir sin avisar sería deshonesto. Se
predice **y** se avisa.

### `TODO 3` — exponer el contrato

```python
@bp.get("/api/model")
def model():
    """El contrato del modelo, tal cual. Alimenta el formulario y la Model Card.

    El frontend no tiene una lista de features escrita a mano: la pide aqui. Si
    el modelo cambia, el formulario cambia solo.
    """
    return jsonify(contrato)
```

Tres líneas que le ahorran a la sesión 3 un formulario escrito a mano.

### `TODO 4` — predecir

```python
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
```

Mira lo que **no** hace este endpoint: no imputa, no escala, no codifica, y no invierte
ningún logaritmo. Le pasa el `DataFrame` crudo al pipeline y devuelve el número. **Si tuviera
que hacer algo de eso, la exportación estaría mal hecha.**

Y los dos códigos de error dicen cosas distintas:

- **`400`** — te equivocaste tú, y te digo exactamente en qué campo.
- **`500`** — nos equivocamos nosotros. El detalle va a los registros del servidor, **no a la
  respuesta**: al cliente no se le entrega el interior de la casa.

### Pruébalo

Empuja desde tu computadora, y **en la instancia**:

```bash
./setup/run sync && ./setup/run restart
./setup/run logs api
```

En los registros debe aparecer `artefacto 1.0.0 cargado (scikit-learn 1.5.2)`. Sal con
`Ctrl+C` y prueba los cuatro casos:

```bash
curl -s localhost:8080/api/health
```

```bash
curl -s -X POST localhost:8080/api/predict \
  -H "Content-Type: application/json" \
  -d @artifacts/example.json
```

Ese último va a fallar con `400`, y **está bien**: `example.json` tiene el input dentro de una
llave `input`, no en la raíz. Mándale sólo el input:

```bash
python3 -c "import json;print(json.dumps(json.load(open('artifacts/example.json'))['input']))" \
  | curl -s -X POST localhost:8080/api/predict -H "Content-Type: application/json" -d @-
```

Y los casos que importan:

```bash
curl -s -X POST localhost:8080/api/predict -H "Content-Type: application/json" \
  -d '{"GrLivArea": 1500}'
```

`400`, diciendo qué feature falta.

---

## 1:40 — El test que importa (12 min)

Un solo test, y es el único de este módulo que no se puede recortar.

**En la instancia:**

```bash
./setup/run test
```

```
   notebook                              servicio
   ────────────────────                  ─────────────────────────
   pipeline.predict(ejemplo)             POST /api/predict
            │                                      │
            ▼                                      ▼
       141,334.96                            141,334.96
            └──────────── ¿iguales? ───────────────┘
```

Si coinciden, la costura está sana. Si no, hay exactamente cuatro causas posibles y el test
te dice cuál:

- el servicio transforma la entrada por su cuenta
- se reemplazó el artefacto sin regenerar `example.json`
- la versión de scikit-learn no es la del entrenamiento
- la inversión del target quedó fuera del artefacto

**Rómpelo a propósito**, para ver que sirve. Cambia un número en `example.json`, empuja,
`sync`, y córrelo otra vez. Debe fallar. Luego revierte.

> Como todo en este módulo, se invoca con `./setup/run` y desde donde sea. Llamar a
> `.venv/bin/python` a mano funciona sólo si estás parado en la raíz del proyecto, y cuando
> no lo estás el error —`No such file or directory`— no dice eso.

> Este test transfiere **igual** a tu reto de clasificación: compara la clase predicha y el
> vector de probabilidades en lugar de un número. Es el mismo test con otro tipo de dato.

---

## 1:52 — Cierre (8 min)

**En tu computadora:**

```bash
git add -A
git commit -m "sesion 2: el modelo cruza la frontera"
git push
```

Y en la consola de AWS: **Instance state → Stop instance**. Detener, no terminar.

Lo que quedó armado:

```
   notebook  ──exporta──▶  artifacts/  ──carga──▶  s2_modelo.py  ──▶  /api/predict
                           pipeline                  valida contra
                           metadata                  el contrato
                           example
                              │
                              └──▶ test_paridad.py comprueba que los dos
                                   extremos dan el mismo número
```

En la sesión 3 esto se vuelve un producto: un formulario que cualquiera puede usar, el
historial de lo que el modelo ha predicho, y una explicación en lenguaje natural.

Pero lo de hoy es lo que te llevas al reto. **La costura es el módulo.**

---

## Si te quedaste atrás

**En tu computadora:**

```bash
./setup/run recuperar 2 --si
git push --force
```

**Y en la instancia:** `./setup/run sync && ./setup/run restart`

Tres cosas que ese comando garantiza, y por eso puedes usarlo sin miedo:

- **No pierdes nada.** Lo que tenías queda en una rama `respaldo/<fecha>`.
- **Conservas tu artefacto.** No tienes que volver a correr el notebook.
- **Se actualiza sola.** Si tu copia de `setup/` es vieja, trae la del curso primero.

> **¿Y si `recuperar` ni siquiera existe en tu copia?** Tres líneas de git puro lo arreglan
> desde cualquier estado:
>
> ```bash
> git fetch https://github.com/vsosahdz/TC3009-Part1-2026.git main
> git checkout FETCH_HEAD -- setup/
> ./setup/run recuperar 2 --si
> ```

