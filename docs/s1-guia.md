# Sesión 1 — La máquina y el contrato

**Dos horas.** Al final vas a tener una máquina Ubuntu propia en la nube, corriendo un
tablero que lee datos reales desde una API que escribiste tú, y accesible desde el navegador
de cualquiera.

Lo que de verdad se aprende hoy es doble: que **el código tiene que viajar hasta donde se
ejecuta**, y que **el frontend y el backend son dos programas distintos que se hablan por un
contrato**.

```
   0:00  ¿por qué un notebook no es un producto?      10 min
   0:10  crear tu instancia EC2                       25 min
   0:35  abrir los puertos                             5 min
   0:40  conectarte, clonar y aprovisionar            15 min
   0:55  el contrato de API                           10 min
   1:05  abrir el proyecto en TU computadora            5 min
   1:10  Flask: los tres endpoints (los escribes tú)   20 min
   1:30  CORS, con el problema delante                10 min
   1:40  el tablero: escribes la costura                15 min
   1:55  cierre y push                                 5 min
```

---

## 0:00 — Por qué un notebook no es un producto (10 min)

Sin código todavía.

```
   TU MÓDULO ANTERIOR              ESTE MÓDULO
  ┌──────────────┐
  │   notebook   │      ╔═══════════════════════════╗
  │   EDA, fit   │─────▶║  ¿qué cruza esta línea?   ║──▶  alguien lo usa
  │   score      │      ╚═══════════════════════════╝
  └──────────────┘
```

Un notebook tiene tres cosas que un producto no puede tener: **estado oculto** (celdas
corridas en desorden), **un solo usuario** (tú), y **ninguna interfaz** (quien no programa no
puede tocarlo).

Y una cuarta que se nota hoy: **corre en tu máquina**. Si tu modelo sólo funciona en tu
laptop, no funciona.

---

## 0:10 — Crear tu instancia (25 min)

Entra al **AWS Academy Learner Lab**, presiona **Start Lab**, espera el punto verde y abre la
consola de AWS. Verifica arriba a la derecha que estás en la región **N. Virginia
(us-east-1)**.

Ve a **EC2 → Instances → Launch instances** y sigue estos campos en orden:

| Campo | Valor |
| ----- | ----- |
| **Name** | `tc3009-tu-nombre` |
| **Application and OS Images** | **Ubuntu Server 24.04 LTS** |
| **Instance type** | **t2.medium** |
| **Key pair (login)** | **Proceed without a key pair** |
| **Configure storage** | **20 GiB**, gp3 — el valor por defecto es 8 y **no alcanza** |

### Cuidado con la versión de Ubuntu

La lista te va a ofrecer una versión **más nueva** que la 24.04 como opción por defecto.
Abre el desplegable y **selecciona 24.04 LTS explícitamente**.

No es capricho: 24.04 es la versión con la que está probado este material, y las versiones
recién liberadas cambian nombres de paquete y versiones de librerías. En un curso de 30
personas, la versión probada vale más que la más reciente.

### Por qué sin key pair

Porque tú nunca vas a conectarte por SSH desde tu computadora. Vas a abrir la terminal desde
el navegador, en la consola de AWS.

### Por qué 20 GB y no los 8 por defecto

Porque en esos 8 GB tienen que caber Ubuntu, el entorno de Python con pandas y
scikit-learn, y `node_modules`. Suman más de lo que parece, y un disco lleno se manifiesta
como errores raros de `npm install` a mitad de la sesión 3.

Cuestan centavos. Súbelo a 20.

### Network settings — presiona **Edit**

- **Auto-assign public IP**: `Enable`
- **Security group**: elige **Select existing security group** y selecciona el grupo
  **`default`**

No crees uno nuevo. Usa el que ya existe en tu cuenta del laboratorio; las reglas se las
agregamos en el siguiente paso.

### Advanced details — el paso que da un plan B

Baja hasta **Advanced details** (viene plegado) y en **IAM instance profile** elige
**`LabInstanceProfile`**.

No es indispensable para conectarte, pero habilita **Session Manager** como segunda vía de
acceso. Si un día *Connect* no te funciona, esa es tu salida. Cuesta un clic y te ahorra
quedarte fuera de tu propia máquina.

Presiona **Launch instance** y espera a que el estado sea `Running` con los checks en verde.

---

## 0:35 — Abrir los puertos (5 min)

Tu instancia ya está corriendo, pero **nadie puede llegarle todavía** — ni tú. El grupo
`default` no trae ninguna regla de entrada.

Ve a **EC2 → Security Groups**, selecciona el grupo **`default`**, y presiona
**Edit inbound rules**. Agrega tres:

| Type | Port | Source | Description |
| ---- | ---- | ------ | ----------- |
| SSH | `22` | `0.0.0.0/0` | conexión desde el navegador |
| Custom TCP | `3000` | `0.0.0.0/0` | tablero (Vite) |
| Custom TCP | `8080` | `0.0.0.0/0` | API (Flask) |

Guarda con **Save rules**.

Un security group es un **firewall**: lo que no abres explícitamente, no entra. Si más tarde
tu tablero "no carga" y el servidor sí está corriendo, este es el primer lugar a revisar.

> `0.0.0.0/0` significa "desde cualquier lugar de internet". Para una clase está bien. En un
> producto real se restringe —el 22 sólo al rango de AWS, el 3000 y 8080 sólo a quien deba
> verlos— y esa es una de las cosas que la Parte 2 arregla.

### El detalle que confunde a todos: ¿SSH abierto, si la red del Tec bloquea SSH?

Porque **el SSH no sale de tu computadora.** Cuando presionas *Connect* en la consola, la
conexión es así:

```
   Tu navegador ──HTTPS──▶ consola de AWS ──SSH──▶ tu instancia
        │                        │                      │
   sale del Tec            ocurre DENTRO           puerto 22
   por el 443              de la red de AWS
```

Tu laptop sólo habla HTTPS con AWS. El salto SSH lo hace AWS contra tu instancia, dentro de
su propia red, donde ninguna política del campus aplica. Por eso funciona.

---

## 0:40 — Conectarte, clonar y aprovisionar (15 min)

En **EC2 → Instances**, selecciona tu instancia y presiona **Connect**. Deja la pestaña
**EC2 Instance Connect** y presiona **Connect**. Se abre una terminal en el navegador.

> Si esa pestaña falla, usa **Session Manager** — es la razón por la que adjuntaste el
> `LabInstanceProfile`.

**En la instancia**, clona **tu fork** —no el repositorio del curso— y corre el
aprovisionamiento:

```bash
cd ~
git clone https://github.com/TU-USUARIO/TC3009-Part1-2026.git
cd TC3009-Part1-2026
bash setup/bootstrap-ec2.sh
```

> Vas a clonar este mismo repositorio **dos veces**: aquí en la instancia, para ejecutarlo, y
> más tarde en tu computadora, para editarlo. Son dos copias con papeles distintos y el mismo
> comando. Que no te confunda.

El script tarda unos cuatro minutos. **Mientras corre**, léelo: instala git, Python, `venv`,
Node, crea el entorno virtual y instala las dependencias. Es la razón por la que las treinta
máquinas del salón son idénticas y la tuya no depende de si usas Windows o Mac.

Cuando termine, comprueba el entorno y averigua tu dirección:

```bash
./setup/run doctor
./setup/run url
```

**Todos los comandos del módulo se invocan así**, con la ruta completa y desde la raíz del
proyecto. No hay abreviaturas: dependerían de que tu terminal haya leído el archivo de
configuración correcto, y cuando eso falla el error es `command not found` sin ninguna
pista de por qué.

La dirección que devuelve `url` es donde vive tu tablero. **Apúntala**: cada vez que el laboratorio
reinicie tu instancia, esa IP cambia.

### Lo único que tienes que recordar de nvm

Node se instaló con **nvm**, que no es un programa sino una **función de shell**. Eso tiene
una consecuencia práctica: en cada terminal nueva hay que cargarlo antes de que `node` y
`npm` existan.

Son las tres líneas que el propio instalador de nvm imprime al terminar:

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"
```

Los comandos del módulo no dependen de esto: `./setup/run` carga nvm por su cuenta. Pero si
quieres usar `node` o `npm` a mano y **ves esto**:

```
   nvm: command not found
   node: command not found
```

...no es que falte instalar nada. Es que esa terminal no leyó tu archivo de arranque. Corre
las tres líneas y sigue.

> Vale la pena entender la diferencia: `python3` es un archivo ejecutable en el disco, y
> siempre está ahí. `nvm` es una función que vive en la memoria de tu shell, y desaparece
> cuando cierras la terminal. Por eso uno "siempre funciona" y el otro hay que cargarlo.

---

## 0:55 — El contrato primero (10 min)

Abre **[docs/api-contrato.md](api-contrato.md)** y léelo con el salón.

La regla del módulo:

> Si el contrato no está escrito, no se escribe código.

Suena burocrático hasta la primera vez que el frontend espera `precio` y el backend manda
`price`. Con dos programas distintos, el contrato es lo único que evita que cada quien
adivine.

Fíjate en un detalle de `/api/data`: un filtro sin resultados devuelve `200` con lista vacía,
**no un error**. Un error es que algo salió mal. Una búsqueda vacía es un resultado legítimo.
Esa distinción vale toda la sesión.

---

## 1:05 — Alto: abre el proyecto en TU computadora (5 min)

Hasta ahora todo ha pasado en el navegador, dentro de tu instancia. **Eso se acaba aquí.**

A partir de este momento trabajas en **dos lugares distintos**, y confundirlos es la causa
número uno de frustración en esta sesión:

```
   TU COMPUTADORA                      TU INSTANCIA EC2
   ────────────────                    ─────────────────
   VS Code                             terminal del navegador
   AQUÍ ESCRIBES CÓDIGO                AQUÍ CORRES COMANDOS
   git add · commit · push             ./setup/run sync · restart · logs

   nunca corres la aplicación          nunca editas archivos
```

> **La regla para no perderte:** si estás en el navegador, estás en la instancia. Si estás en
> VS Code, estás en tu computadora. Nunca edites archivos en la instancia — lo que escribas
> ahí lo va a borrar el siguiente `sync`.

### Abre una ventana nueva, en tu propia máquina

Si ya clonaste tu fork en la tarea previa, ábrelo:

```bash
cd TC3009-Part1-2026
code .
```

Si no lo hiciste, hazlo ahora — **en una terminal de tu computadora**, no en el navegador:

```bash
git clone https://github.com/TU-USUARIO/TC3009-Part1-2026.git
cd TC3009-Part1-2026
code .
```

### Comprueba que estás donde crees

En la terminal de VS Code:

```bash
git remote -v
```

Debe decir **tu usuario**, no `vsosahdz`. Si dice `vsosahdz`, clonaste el repositorio del
curso en lugar de tu fork: vas a poder trabajar toda la sesión y el `git push` del final va a
fallar. Mejor arreglarlo ahora.

### Por qué así y no editando en la instancia

Porque escribir React en `nano`, dentro de una terminal de navegador, sin resaltado ni
autocompletado, es miserable. Y porque el ciclo `push` → `pull` es lo que hace un equipo real:
tu código **viaja** hasta donde se ejecuta. No es una molestia del curso, es el trabajo.

---

## 1:10 — Flask: los tres endpoints (20 min)

Aquí empieza el ciclo que vas a usar el resto del módulo:

```
   1. Editas backend/s1_tablero.py en VS Code, en tu laptop
   2. git add · git commit · git push
   3. En la consola de la instancia:  ./setup/run sync
   4. Y para que corra el codigo nuevo:  ./setup/run restart
```

Esos dos últimos comandos son el ciclo entero. Te los vas a saber de memoria.

**En la instancia** (la terminal del navegador), levanta los servidores. Se van a segundo
plano, así que tu única consola queda libre:

```bash
./setup/run start
```

> La consola del navegador es una sola, y un servidor en primer plano te la ocuparía. Por eso
> `start` los deja corriendo detrás y te devuelve el prompt. Si algo no responde:
> `./setup/run logs`.

**En tu computadora**, abre `backend/s1_tablero.py` en VS Code. Tiene dos `TODO` por llenar.

Fíjate en la estructura del backend antes de escribir:

```
   backend/
   ├── app.py           el ensamblador. NO lo edites
   ├── s1_tablero.py    ← lo de hoy
   └── s2_modelo.py     la sesión que viene
```

`app.py` descubre solo los módulos `sN_*.py` y registra sus rutas. Por eso cada sesión vive
en su propio archivo: cuando traigas el material de la siguiente, llegan archivos **nuevos**
y nunca hay que fusionar cambios sobre lo que ya escribiste.

---

### Antes de escribir: mira lo que ya está resuelto

Abre `backend/app.py` —sólo para leerlo— y busca estas dos líneas:

```python
ORIGEN_DESARROLLO = re.compile(r"^http://[A-Za-z0-9.\-]+:3000$")
CORS(app, origins=[ORIGEN_DESARROLLO])
```

Es lo que autoriza a tu tablero a pedirle datos a tu API. Al rato lo vemos con el problema
delante; por ahora sólo ten presente que existe y que **no lo tienes que escribir**.

### `/api/health` ya responde — míralo antes de escribir

Vive en `app.py` y ya funciona. Su forma es la que van a tener los tuyos: un decorador con la
ruta, una función, y un `jsonify` que devuelve **exactamente lo que promete el contrato**.

La única diferencia en tu módulo es que el decorador es `@bp.get(...)` en lugar de
`@app.get(...)`: `bp` es el blueprint de este módulo, y `app.py` lo registra solo.

Compruébalo **en la instancia**:

```bash
curl http://localhost:8080/api/health
```

Es el endpoint más aburrido y el más útil: cuando algo falle, es el primero que vas a
consultar.

---

### `/api/stats` — los agregados

**En tu computadora**, reemplaza el `TODO` de `/api/stats` con esto:

```python
@bp.get("/api/stats")
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
```

Guarda. **En tu computadora**, empuja el cambio:

```bash
git add -A && git commit -m "endpoint de agregados" && git push
```

**En la instancia**, tráelo y relanza:

```bash
./setup/run sync && ./setup/run restart
curl -s http://localhost:8080/api/stats | head -c 300
```

**Debe decir `"count": 1460`.** Si dice otra cosa, algo se quedó a medias.

Tres cosas que vale la pena mirar en lo que acabas de escribir:

- **`int()` y `float()` no son adorno.** Los tipos que devuelve pandas son de numpy, y `jsonify`
  no sabe convertirlos. Si los quitas, el servidor truena con
  `Object of type int64 is not JSON serializable`. Es el error más común de este bloque.
- **`by_neighborhood` se calcula sobre `df`, no sobre `alcance`.** A propósito: es el eje de
  comparación del tablero. Si lo filtraras, al elegir una colonia te quedaría una sola barra,
  y una barra sola no compara nada.
- **Una colonia sin registros devuelve `200`, no un error.** Un error es que algo salió mal;
  una búsqueda vacía es un resultado legítimo. Esa distinción está en el contrato y ahora está
  en tu código.

---

### `/api/data` — los registros

**En tu computadora**, reemplaza el `TODO` de `/api/data`:

```python
@bp.get("/api/data")
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
```

Mismo ciclo: **en tu computadora** `git add -A && git commit -m "endpoint de registros" &&
git push`; **en la instancia** `./setup/run sync && ./setup/run restart`. Y ahora sí, pruébalo
en serio, en la instancia:

```bash
curl -s "http://localhost:8080/api/data?neighborhood=NAmes&limit=3" | head -c 300
```

`total_matching` debe ser **225**.

Y el caso que de verdad importa:

```bash
curl -s -w "\n[http %{http_code}]\n" "http://localhost:8080/api/data?neighborhood=NoExiste"
```

`200` con `rows: []`. Como dice el contrato.

> **Las diez columnas de `EXPOSED_COLUMNS` no son al azar:** son exactamente las features que
> el modelo va a usar en la sesión 2. El tablero y el predictor hablan el mismo vocabulario
> desde hoy, y eso no fue casualidad.

Con esto tu backend está completo. Lo escribiste tú.

---

## 1:30 — CORS, con el problema delante (10 min)

Tu tablero va a correr en el puerto **3000** y tu API en el **8080**. Para el navegador,
**eso son dos sitios distintos**, y por defecto no deja que uno lea al otro.

Compruébalo. La misma petición, cambiando quién dice ser:

```bash
curl -s -D - -o /dev/null -H "Origin: http://localhost:3000" \
  http://localhost:8080/api/health | grep -i "access-control"
```

```bash
curl -s -D - -o /dev/null -H "Origin: http://evil.example:9999" \
  http://localhost:8080/api/health | grep -i "access-control"
```

La primera devuelve `Access-Control-Allow-Origin`. La segunda no devuelve nada. Esa cabecera
es el permiso, y **el navegador es quien lo exige** — `curl` no, por eso las dos "funcionan"
desde la terminal.

En `backend/app.py` el permiso se da por patrón, no por dirección:

```python
ORIGEN_DESARROLLO = re.compile(r"^http://[A-Za-z0-9.\-]+:3000$")
CORS(app, origins=[ORIGEN_DESARROLLO])
```

¿Por qué un patrón y no la IP de tu instancia? Porque **esa IP cambia cada vez que el
laboratorio te reinicia la máquina**. Una dirección escrita a mano dejaría de funcionar en la
siguiente sesión, y el síntoma sería un error de red imposible de rastrear.

> **Esto desaparece en producción.** En la sesión 4, un solo contenedor sirve el tablero y la
> API desde el mismo origen, y CORS deja de existir. El problema es del desarrollo, no del
> producto.

---

## 1:40 — El tablero: escribe la costura (15 min)

El tablero ya está en el repositorio: `App.jsx`, las gráficas, la tabla, los estilos. Eso es
presentación, enseña poco, y no cabe teclearla en quince minutos.

**Pero no funciona.** Le falta una pieza, y es justo la que importa:

```
   App.jsx  ──importa──▶  api.js  ──fetch──▶  tu API en :8080
                            ▲
                     esto lo escribes tú
```

`frontend/src/api.js` está a medias. Es la **costura** entre las dos mitades del producto: el
único lugar del frontend que sabe que existe un backend.

**En tu computadora**, ábrelo en VS Code y mira lo que ya está:

```javascript
const API_BASE = `http://${window.location.hostname}:8080`;
```

Esa línea es la más importante del archivo. **La dirección no está escrita a mano**, sale de
dónde se cargó la página. ¿Por qué? Porque la IP de tu instancia cambia cada vez que el
laboratorio la reinicia. Si aquí hubiera un número, tu tablero funcionaría hoy y estaría roto
la próxima sesión, con un error de red que no dice nada.

**En tu computadora**, reemplaza los dos `TODO` con esto:

```javascript
async function get(path, params = {}) {
  const url = new URL(API_BASE + path);
  Object.entries(params).forEach(([clave, valor]) => {
    if (valor !== null && valor !== undefined && valor !== "") {
      url.searchParams.set(clave, valor);
    }
  });

  const respuesta = await fetch(url);
  if (!respuesta.ok) {
    throw new Error(`${respuesta.status} al pedir ${path}`);
  }
  return respuesta.json();
}

export const getHealth = () => get("/api/health");
export const getStats = (neighborhood) => get("/api/stats", { neighborhood });
export const getData = (neighborhood, limit = 20) =>
  get("/api/data", { neighborhood, limit });
```

Guarda y empuja **desde tu computadora**:

```bash
git add -A && git commit -m "la costura al backend" && git push
```

**En la instancia**:

```bash
./setup/run sync && ./setup/run restart
./setup/run url
```

Abre esa dirección en tu navegador. **El tablero entero cobra vida de golpe**: las tarjetas,
las dos gráficas, la tabla y el filtro. Todo eso estaba esperando estas veinte líneas.

### Tres cosas que acabas de resolver sin darte cuenta

**Los parámetros vacíos se omiten.** Sin ese `if`, al no haber filtro mandarías
`?neighborhood=` con valor vacío, y tu backend filtraría por la colonia llamada "" — cero
resultados. El tablero aparecería vacío y el error estaría en el frontend, no en el backend.

**Un código que no es 200 lanza un error.** Sin eso, `fetch` no falla: te devuelve la respuesta
de error y `App.jsx` intentaría leer datos que no existen. La pantalla quedaría en blanco sin
explicación. Con el `throw`, la interfaz puede mostrar qué pasó.

**Los nombres exportados importan.** `App.jsx` importa `getStats` y `getData` con esos nombres
exactos. Es un contrato, igual que el de la API — sólo que entre dos archivos en lugar de
entre dos programas.

### Y ahora que funciona, mira el filtro

Elige una colonia. Las tarjetas y la gráfica de calidad se recalculan, pero **la gráfica de
colonias no se filtra: resalta la elegida.**

Eso lo decidiste tú cuando escribiste `/api/stats` con `by_neighborhood` sobre `df` completo.
No fue un detalle técnico: **filtrar no siempre significa ocultar**, y ésa es la primera
decisión de producto del módulo.

---

## 1:55 — Cierre (5 min)

**En tu computadora**:

```bash
git add -A
git commit -m "sesion 1: API del tablero"
git push
```

**El push no es opcional.** Tu código vive en una máquina que puede perderse —un reset del
laboratorio, el presupuesto agotado— y GitHub es la única copia que sobrevive.

Y en la consola de AWS: selecciona tu instancia y **Instance state → Stop instance**.

> **Detener, no terminar.** Esta máquina es tu entorno de trabajo de las cuatro sesiones. Si
> la terminas, pierdes el aprovisionamiento y hay que rehacerlo. El laboratorio la va a
> reiniciar sola la próxima sesión, con **una IP nueva** — por eso nada apunta a una
> dirección fija.

Lo que quedó armado hoy:

```
   tu navegador ──▶ EC2 :3000 (React) ──fetch──▶ EC2 :8080 (Flask) ──▶ train.csv
                        ▲                            │
                        │                            └── CORS autoriza el origen
                   security group
                   abre 3000 y 8080
```

En la sesión 2, entre Flask y la respuesta aparece **el modelo**. Todo lo demás se queda
igual. Por eso hoy importaba el contrato: mañana cambia lo de adentro y el contrato aguanta.

---

## Si te quedaste atrás

**En tu computadora:**

```bash
./setup/run recuperar 1 --si
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
> ./setup/run recuperar 1 --si
> ```

Te deja en el estado correcto al cierre de esta sesión. Sin vergüenza: es más rápido que
depurar en vivo, y es para lo que existen los checkpoints.
