# Sesión 4 — Memoria, palabras y un origen de verdad

**Dos horas.** Hoy el producto deja de ser amnésico.

Al cerrar la sesión 3 tenías una interfaz que cualquiera puede usar. Pero cierra la pestaña y
no queda rastro de lo que predijo: nadie puede auditar una decisión, nadie sabe si alguien lo
está usando, y nadie puede comprobar si el modelo se está quedando viejo.

Y tus datos siguen siendo un CSV dentro del repositorio.

```
   0:00  lo que un producto sin memoria no puede contestar   10 min
   0:10  el servicio gana memoria                            40 min
   0:50  el historial                                        15 min
   1:05  la base de datos como origen                        45 min
   1:50  cierre                                              10 min
```

> **La segunda mitad —PostgreSQL— todavía se está construyendo.** Este documento cubre la
> primera: el registro de predicciones, la explicación y la vista de historial.

---

## Antes de empezar

**En tu computadora:**

```bash
git add -A && git commit -m "cierre de la sesión 3"
./setup/run actualizar 4
git push
```

**Y en la instancia:** `./setup/run sync`

Lo que llega:

```
    nuevo        backend/s4_producto.py              el módulo de hoy, con 4 TODO
    nuevo        frontend/src/vistas/Historial.jsx   la tabla, con 2 TODO
    conservado   frontend/src/api.js                 (ya lo tienes)
    conservado   frontend/src/vistas/Predecir.jsx    (ya lo tienes)
```

Fíjate en las dos últimas: el frontend de la sesión 3 **no se toca hoy**. Ya lo dejaste listo
—`explicar` y `getHistory` están escritas desde ayer— y en cuanto el backend exista, la
explicación va a aparecer sola debajo del precio. No vas a editar `Predecir.jsx` ni una vez.

### ¿No estuviste en la sesión 3?

**En tu computadora:**

```bash
./setup/run recuperar 3 --si
git push --force
```

**Y en la instancia:** `./setup/run sync && ./setup/run restart`

Conserva tu artefacto. Si no tienes uno, corre el notebook de la sesión 2 en paralelo.

---

## 0:00 — Lo que un producto sin memoria no puede contestar (10 min)

Tu API predice bien y tiene interfaz. Preguntas que **no** sabe contestar:

| Pregunta | ¿Por qué importa? |
|---|---|
| ¿Cuántas predicciones llevas hoy? | Sin esto no sabes si alguien lo está usando |
| ¿Qué predijiste la semana pasada? | Sin esto no puedes auditar una decisión |
| ¿Los datos que te llegan se parecen a los del entrenamiento? | Sin esto no detectas que el modelo se está quedando viejo |
| ¿Por qué este precio y no otro? | Sin esto nadie va a confiar en el número |

Las cuatro se contestan con **dos cosas**:

```
   MEMORIA    cada predicción queda registrada, y se puede consultar
   PALABRAS   la predicción se explica, no solo se entrega
```

Ninguna de las dos cambia el modelo. Las dos cambian el producto.

Y las dos necesitan algo que hasta ahora no tenías: **un lugar donde guardar cosas.** Hoy va a
ser un archivo SQLite junto al código — y en la segunda mitad de la sesión vas a ver por qué
eso no alcanza, y qué lo reemplaza.

---

## 0:10 — El servicio gana memoria (40 min)

Abre [backend/s4_producto.py](../backend/s4_producto.py).

Antes de escribir nada, **lee el archivo completo**. Hay cuatro TODO, pero lo más importante
del archivo ya está escrito, y es esto:

```python
@bp.after_app_request
def registrar_si_fue_prediccion(respuesta):
```

Párate ahí un momento.

### El gancho: agregar sin modificar

Necesitamos que cada llamada a `/api/predict` quede guardada. Pero `/api/predict` lo
escribiste **tú** en la sesión 2, en `s2_modelo.py`, y no queremos volver a abrir ese
archivo: editarlo obligaría a fusionar cambios sobre código que ya es tuyo, y ahí es donde
aparecen los conflictos.

`@bp.after_app_request` deja mirar —y reaccionar a— **cualquier respuesta de la aplicación**,
venga del módulo que venga:

```python
    if request.path != "/api/predict" or respuesta.status_code != 200:
        return respuesta

    try:
        datos = respuesta.get_json()
        registrar(
            datos["prediction_id"],
            datos["model_version"],
            datos["prediction"],
            request.get_json(silent=True) or {},
        )
    except Exception:  # noqa: BLE001
        # Que falle el registro NO debe tumbar una prediccion que ya salio
        # bien. El usuario ya tiene su numero; el log es cosa nuestra.
        current_app.logger.exception("no se pudo registrar la prediccion")

    return respuesta
```

Tres decisiones en doce líneas:

1. **Un 400 no se registra.** Solo hay predicción cuando hubo predicción. Si registraras los
   errores en la misma tabla, cualquier conteo que hagas después estaría mal.
2. **Se guarda la petición, no solo la respuesta.** `request.get_json()` — el input completo.
   Vuelvo a esto en un momento.
3. **Si el registro truena, la predicción sobrevive.** El usuario ya tiene su número. Que tu
   bitácora falle no es razón para devolverle un 500.

La idea —*agregar comportamiento sin modificar lo que ya funciona*— la vas a reencontrar como
middleware, interceptores o decoradores en casi cualquier framework. Es la que quieres copiar
en tu reto.

### `TODO 1` — la tabla

```python
def crear_esquema():
    with conectar() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS predicciones (
                prediction_id TEXT PRIMARY KEY,
                creado_en     TEXT NOT NULL,
                model_version TEXT NOT NULL,
                prediccion    REAL NOT NULL,
                entrada       TEXT NOT NULL
            )
            """
        )
```

`IF NOT EXISTS` la hace idempotente: se llama en cada arranque y no pasa nada.

La columna que importa es la última. **Se guarda el input completo, no solo el resultado.**

Cuesta lo mismo hoy, y es la que hace posible, más adelante, comparar lo que el modelo está
viendo contra lo que vio al entrenar. Eso es detección de *drift*, y sin los inputs no hay
nada que comparar. Es la diferencia entre "el modelo lleva seis meses en producción" y "el
modelo lleva seis meses en producción y sé que sigue sirviendo".

⚠ Nota de producto: registrar entradas crudas tiene implicaciones de datos personales en un
sistema real. Aquí son casas; en tu reto puede que no.

### `TODO 2` — el INSERT

```python
def registrar(prediction_id, model_version, prediccion, entrada):
    with conectar() as con:
        con.execute(
            "INSERT OR REPLACE INTO predicciones VALUES (?, ?, ?, ?, ?)",
            (
                prediction_id,
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                model_version,
                float(prediccion),
                json.dumps(entrada, ensure_ascii=False),
            ),
        )
```

Tres detalles:

- **Los `?` no son opcionales.** Armar el SQL con formato de cadena es inyección de SQL, y da
  igual que esto sea un ejercicio: es el hábito lo que se está formando.
- **La hora la pone el servidor, en UTC.** Nunca el cliente: el reloj del cliente puede estar
  en otra zona, mal puesto, o mentir.
- **`entrada` es un diccionario y la columna es TEXT.** `json.dumps` para entrar,
  `json.loads` para salir.

Reinicia y comprueba que la tabla ya existe:

```bash
./setup/run restart
curl -s http://localhost:8080/api/health
```

Ahora `"status":"ok"` y aparece `"predicciones_registradas":0`.

Predice algo y vuelve a mirar:

```bash
curl -s -X POST http://localhost:8080/api/predict \
  -H 'Content-Type: application/json' \
  -d '{"GrLivArea":1144,"OverallQual":5,"YearBuilt":1963,"TotalBsmtSF":1144,
       "GarageCars":1,"FullBath":1,"BedroomAbvGr":3,"LotArea":9204,
       "Neighborhood":"NAmes","KitchenQual":"TA"}'

curl -s http://localhost:8080/api/health
```

`predicciones_registradas` pasó a 1, y **no tocaste `s2_modelo.py`**. Eso es el gancho
funcionando.

Prueba ahora con una entrada inválida y vuelve a contar: sigue en 1.

### `TODO 3` — el historial

```python
@bp.get("/api/history")
def history():
    try:
        limite = int(request.args.get("limit", 50))
    except ValueError:
        limite = 50
    limite = max(1, min(limite, 500))

    with conectar() as con:
        filas = con.execute(
            "SELECT * FROM predicciones ORDER BY creado_en DESC, rowid DESC LIMIT ?",
            (limite,),
        ).fetchall()

    return jsonify(
        {
            "count": len(filas),
            "rows": [
                {
                    "prediction_id": f["prediction_id"],
                    "created_at": f["creado_en"],
                    "model_version": f["model_version"],
                    "prediction": round(f["prediccion"], 2),
                    "input": json.loads(f["entrada"]),
                }
                for f in filas
            ],
        }
    )
```

Dos cosas que no son decoración:

- **`limite` se acota entre 1 y 500.** Nunca dejes que el cliente pida "todo". Hoy son cuatro
  filas; el día que sean cuatro millones, ese `min()` es lo único que separa tu API de un
  servidor caído.
- **El orden desempata con `rowid`.** Dos predicciones en el mismo segundo tienen el mismo
  `creado_en`, y sin el desempate el orden sería arbitrario entre ejecuciones.

Y un detalle de diseño: el historial se llama `/api/history`, no `/api/predictions`. Es lo
que el **producto** muestra, no la tabla que hay debajo. Si mañana el almacenamiento cambia a
PostgreSQL —que es exactamente lo que pasa en la sesión 4— la URL no se entera.

### `TODO 4` — la explicación

```python
def redactar(entrada, prediccion):
    contrato = s2_modelo.contrato
    importancias = contrato.get("feature_importances", {})
    top = [f for f, _ in sorted(importancias.items(), key=lambda kv: -kv[1])[:3]]

    partes = []
    for nombre in top:
        valor = entrada.get(nombre)
        if valor is None:
            continue
        ficha = next((f for f in contrato["features"] if f["name"] == nombre), None)
        if ficha and ficha["type"] == "num" and "median" in ficha:
            mediana = ficha["median"]
            if valor > mediana * 1.15:
                partes.append(f"{nombre} por encima de lo habitual ({valor:g})")
            elif valor < mediana * 0.85:
                partes.append(f"{nombre} por debajo de lo habitual ({valor:g})")
            else:
                partes.append(f"{nombre} en el rango habitual ({valor:g})")
        else:
            partes.append(f"{nombre} = {valor}")

    detalle = "; ".join(partes) if partes else "los datos proporcionados"
    return (
        f"El modelo estima {prediccion:,.0f} para esta casa. "
        f"Lo que mas pesa en esa estimacion es {detalle}."
    )
```

No hay ningún modelo de lenguaje aquí. Es una plantilla, y sale toda del contrato: las tres
features que más pesan, comparadas contra la mediana que `metadata.json` ya traía.

Mira el endpoint que ya está escrito, `/api/explain`. Lo importante es lo que **no** hace:

```python
    entrada = payload.get("input")
    prediccion = payload.get("prediction")
```

**Recibe la predicción. No la recalcula.** Si esta función corriera el modelo por su cuenta,
podría darte 140,637 mientras el usuario está viendo 140,638 en pantalla —por un redondeo, o
porque entre una llamada y otra se recargó otro artefacto— y entonces la explicación
contradice al producto. La regla del principio de la sesión, aplicada.

En [docs/extras/gemini-explain.md](extras/gemini-explain.md) está documentado cómo cambiar
esto por un modelo de lenguaje de verdad. Fíjate en que el cambio es **reemplazar esta sola
función**: el contrato de `/api/explain` no se mueve.

```bash
./setup/run restart
curl -s -X POST http://localhost:8080/api/explain \
  -H 'Content-Type: application/json' \
  -d '{"input":{"OverallQual":5,"GrLivArea":1144,"TotalBsmtSF":1144},"prediction":140637.5}'
```

```json
{"explanation":"El modelo estima 140,638 para esta casa. Lo que mas pesa en esa estimacion
 es OverallQual por debajo de lo habitual (5); GrLivArea por debajo de lo habitual (1144);
 TotalBsmtSF por encima de lo habitual (1144).","source":"plantilla"}
```

Tres features, tres comparaciones contra la mediana del dataset. Nota que `TotalBsmtSF` con
1144 sale "por encima" apenas: la mediana es 991.5 y el umbral está en 15% arriba. Esos
cortes son una decisión tuya, no del modelo — y como son tuyos, se pueden explicar.

El backend está listo. Ahora la parte visible.

---

## 0:50 — El historial (15 min)

Abre [frontend/src/vistas/Historial.jsx](../frontend/src/vistas/Historial.jsx).

### `TODO 5` — pedir los datos

```javascript
  useEffect(() => {
    getHistory(50).then(setDatos).catch((e) => setError(e.message));
  }, []);
```

Una línea. Es el mismo patrón del tablero de la sesión 1, y a estas alturas debería aburrirte:
eso es exactamente lo que se buscaba.

### `TODO 6` — la tabla

```javascript
        {datos.rows.length === 0 ? (
          <div className="vacio">
            Todavía no hay ninguna. Ve a <strong>Predecir</strong> y estima un
            precio: va a aparecer aquí.
          </div>
        ) : (
          <div className="scroll-x">
            <table>
              <thead>
                <tr>
                  <th className="txt">Cuándo</th>
                  <th className="txt">Colonia</th>
                  <th>Superficie</th>
                  <th>Calidad</th>
                  <th>Estimado</th>
                  <th className="txt">Modelo</th>
                </tr>
              </thead>
              <tbody>
                {datos.rows.map((f) => (
                  <tr key={f.prediction_id}>
                    <td className="txt">{cuando(f.created_at)}</td>
                    <td className="txt">{f.input.Neighborhood}</td>
                    <td>{Number(f.input.GrLivArea).toLocaleString()}</td>
                    <td>{f.input.OverallQual}</td>
                    <td>{pesos(f.prediction)}</td>
                    <td className="txt mono">{f.model_version}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
```

El estado vacío no dice "sin datos". **Dice qué hacer.** El usuario que acaba de llegar no
sabe que el historial se llena desde la otra pestaña, y un "sin datos" lo deja mirando una
caja gris. Es media línea de código y es la diferencia entre una pantalla muerta y una que
enseña a usarse.

La columna `model_version` parece de relleno hoy, porque todo dice `1.0.0`. No lo es: el día
que entrenes otra versión, esta columna es la que te deja comparar lo que predecía la vieja
contra lo que predice la nueva **sobre las mismas casas**. Sin ella tienes un montón de
números sin saber quién los dijo.

### Ciérralo

Ve a **Predecir**, estima un precio, y vuelve a **Historial**. Ahí está, hasta arriba.

Ese ciclo —pedir, registrar, consultar— es el producto. Lo demás es presentación.

---

---

## 1:05 — La base de datos como origen (45 min)

*(En construcción. Aquí el CSV se muda a PostgreSQL en RDS, y vas a comprobar que ningún
endpoint se entera del cambio.)*

---

## Si te quedaste atrás

**En tu computadora:**

```bash
./setup/run recuperar 4 --si
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
> ./setup/run recuperar 4 --si
> ```

