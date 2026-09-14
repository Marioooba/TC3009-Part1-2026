# Sesión 3 — El producto

**Dos horas, todas de frontend.** Hoy sale del `curl`.

Al terminar la sesión 2 tenías un modelo que responde bien a `/api/predict` — pero solo si
sabes escribir JSON en una terminal. Eso no es un producto, es un endpoint. Hoy alguien que
no sabe qué es un endpoint va a poder usar tu modelo.

El backend **no se toca**: todo lo de hoy consume lo que ya escribiste. El modelo tampoco:
el artefacto que exportaste en la sesión 2 es exactamente el mismo al terminar hoy.

```
   0:00  qué le falta a esto para ser un producto        8 min
   0:08  traer el material de la sesión                  7 min
   0:15  la costura: lo que le falta a api.js           15 min
   0:30  el ensamblador del frontend                    10 min
   0:40  el formulario que sale del contrato            40 min   ← el corazón
   1:20  la Model Card, que ya viene hecha              10 min
   1:30  la prueba que importa                          12 min
   1:42  usarlo de verdad                               10 min
   1:52  cierre                                          8 min
```

> **Qué NO está hoy.** El historial de predicciones y la explicación en lenguaje natural
> pasaron a la sesión 4, donde encajan mejor: ahí el almacenamiento es el tema. Hoy el
> objetivo es uno solo y se cumple entero — **que tu modelo tenga una interfaz que alguien
> pueda usar.**

---

## Antes de empezar: ¿no estuviste en la sesión 2?

**En tu computadora**, en la carpeta del proyecto:

```bash
./setup/run recuperar 2 --si
git push --force
```

**Y luego en la instancia:**

```bash
./setup/run sync
./setup/run start
```

> **Por qué en tu computadora y no en la instancia.** La instancia clonó por HTTPS y no tiene
> credenciales de GitHub: **solo puede hacer `pull`**. Si recuperas ahí, la aplicación te queda
> bien pero tu fork se queda atrás, y el siguiente `push` desde tu computadora te devuelve al
> estado viejo. El flujo va en una sola dirección:
>
> ```
>    Tu computadora  ─push──▶  tu fork  ─pull──▶  Tu instancia
> ```
>
> Todo lo que cambie el código va del lado izquierdo. Si ya lo corriste en la instancia, no
> pasa nada: hazlo también en tu computadora y `sync` en la instancia.

Eso te deja con las sesiones 1 y 2 completas. Pero **falta tu artefacto**: el curso no
manda `artifacts/pipeline.joblib`, porque cada quien genera el suyo (si el curso enviara
uno, chocaría con el tuyo en cada `git pull`).

Corre el notebook de la sesión 2 en Colab —[notebooks/01-entrenar-y-exportar.ipynb](../notebooks/01-entrenar-y-exportar.ipynb)—,
descarga el zip y descomprímelo en `artifacts/`. Son unos 10 minutos y se pueden hacer en
paralelo mientras sigues esta guía: el backend de hoy no arranca sin artefacto, así que
hazlo antes de llegar a la marca de los 15 minutos.

El artefacto **no** se sube a tu fork desde la instancia: como todo lo demás, va de tu
computadora a GitHub. Si lo generaste en Colab, descomprímelo en `artifacts/` **en tu
computadora**, haz `git push`, y `./setup/run sync` en la instancia.

---

## 0:00 — Qué le falta a esto para ser un producto (8 min)

Tu API de la sesión 2 predice bien. Así se usa hoy:

```bash
curl -s -X POST http://localhost:8080/api/predict \
  -H 'Content-Type: application/json' \
  -d '{"GrLivArea":1144,"OverallQual":5,"YearBuilt":1963,"TotalBsmtSF":1144,
       "GarageCars":1,"FullBath":1,"BedroomAbvGr":3,"LotArea":9204,
       "Neighborhood":"NAmes","KitchenQual":"TA"}'
```

Pregúntate quién puede hacer eso. Tiene que saber qué es un endpoint, qué es JSON, los diez
nombres de campo **exactos**, y tener una terminal abierta. Un agente inmobiliario no va a
hacerlo. Tu compañero de equipo tampoco, si no fue él quien escribió la API.

> Un modelo al que solo se llega con `curl` no está terminado. Está **disponible**, que no
> es lo mismo.

Hoy construyes lo que falta:

```
   Un formulario     para pedir el precio sin saber qué es un endpoint
   Una Model Card    para justificar el modelo sin abrir el notebook
```

El formulario es la sesión entera. Y no va a tener los diez campos escritos a mano: **se
construye solo, leyendo el contrato del modelo.** Esa es la idea que te llevas al reto.

### Una regla que no se rompe hoy

> El modelo **decide** el número.
> Todo lo que construyas hoy lo **presenta**.
> Nada de lo de hoy lo **cambia**.

Suena obvio y se rompe todo el tiempo: un redondeo en el frontend, un "si sale negativo pon
cero", una explicación que recalcula por su cuenta. En cuanto la capa de presentación
empieza a decidir, ya tienes dos modelos y solo mediste uno.

### Dónde cae esto en la rúbrica de tu reto

El renglón que dice **"genera una interfaz"** es literalmente esta sesión. Pero hay más: la
Model Card que vas a tener al final es la **superficie de evidencia** de casi todos los demás
renglones —qué modelo elegiste, cómo separaste los datos, qué métricas usaste, qué features
pesan— y está hecha de manera que se llena sola desde `metadata.json`. Cuando cambies al
modelo de clasificación de tu reto, la página se actualiza sin que toques el frontend.

---

## 0:08 — Traer el material de la sesión (7 min)

**En tu computadora:**

```bash
git add -A && git commit -m "cierre de la sesión 2"
./setup/run actualizar 3
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

Guarda y súbelo:

```bash
git add -A && git commit -m "material de la sesión 3"
git push
```

**Y en la instancia:**

```bash
./setup/run sync
```

Lo que llega:

```
    nuevo        frontend/src/vistas/Tablero.jsx     tu tablero, mudado de casa
    nuevo        frontend/src/vistas/Predecir.jsx    el formulario, con 3 TODO
    nuevo        frontend/src/vistas/ModelCard.jsx   completa, de regalo
    actualizado  frontend/src/main.jsx               ahora es un ensamblador
    conservado   backend/s1_tablero.py  (ya lo tienes)
    conservado   backend/s2_modelo.py   (ya lo tienes)
    conservado   frontend/src/api.js    (ya lo tienes)
```

Todo es frontend. **El backend no recibe ni una línea hoy** — y aun así vas a terminar con
algo que no se parece en nada a lo que tenías. Esa es la sesión.

Fíjate en las dos últimas líneas: **tu código de las sesiones 1 y 2 no se tocó.** Eso no es
casualidad, está declarado en [setup/archivos-del-curso.txt](../setup/archivos-del-curso.txt).

Y fíjate en `main.jsx`, que sí se sobreescribió. Es el único archivo del frontend que cambia,
y cambia porque **nunca lo escribiste tú**: llegó hecho en la sesión 1. Es un ensamblador,
igual que `backend/app.py`. Los ensambladores son del curso; tu código es tuyo.

Si en `frontend/src/` te queda un `App.jsx` de las sesiones anteriores, ya no se usa: su
contenido —el tablero— vive ahora en `frontend/src/vistas/Tablero.jsx`. Puedes borrarlo.

Ahora arranca lo que ya funciona, **en la instancia**:

```bash
./setup/run start
./setup/run status
```

⚠ **La página va a salir en blanco.** Es lo esperado, y se arregla en el siguiente bloque.
Abre la consola del navegador (F12):

```
The requested module '/src/api.js' does not provide an export named 'getModel'
```

Las vistas nuevas importan funciones de `api.js` que todavía no escribes. Nota que el
mensaje **dice exactamente qué falta y dónde** — no "algo salió mal". Guárdalo: una pantalla
en blanco con la consola cerrada es el error más caro de todo el módulo, porque no tiene
síntoma. Con la consola abierta tiene nombre y apellido.

Mientras tanto, el backend responde igual que ayer:

```bash
curl -s http://localhost:8080/api/health
```

```json
{"api_version":"1.0.0","artifact_hash":"6ff94a85591c","model_version":"1.0.0",
 "sklearn_version":"1.5.2","status":"ok"}
```

`ok`, como debe ser: hoy no le tocaste nada.

---

## 0:15 — La costura: lo que le falta a `api.js` (15 min)

Abre [frontend/src/api.js](../frontend/src/api.js).

Este archivo es **tuyo** desde la sesión 1 — por eso `actualizar 3` lo dejó intacto, y por eso
hoy no te llega ningún esqueleto que llenar: le vas a **agregar** un bloque al final, debajo
de `getData`.

En la sesión 1 fue **la costura**: el único lugar del frontend que sabe que existe un backend.
Sigue siéndolo, y hoy le faltan cuatro cosas. Dos de ellas son POST, y hasta ahora solo sabe
hacer GET.

### `TODO 5` — el helper y las cuatro funciones

Pega esto al final del archivo:

```javascript
// --- Sesion 3 ---

async function post(path, cuerpo) {
  const respuesta = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo),
  });
  const datos = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) {
    // El backend dice QUE campo esta mal. Ese mensaje es para el usuario,
    // asi que se propaga tal cual en lugar de un "error 400" generico.
    throw new Error(datos.error || `${respuesta.status} al pedir ${path}`);
  }
  return datos;
}

export const getModel = () => get("/api/model");
export const predecir = (entrada) => post("/api/predict", entrada);
export const explicar = (entrada, prediccion) =>
  post("/api/explain", { input: entrada, prediction: prediccion });
export const getHistory = (limit = 50) => get("/api/history", { limit });
```

El detalle que vale la sesión es el `if (!respuesta.ok)`.

En la sesión 2 te tomaste el trabajo de que `/api/predict` dijera *qué* campo está mal:

```
'Neighborhood' no acepta el valor 'Polanco'. Valores validos: Blmngtn, Blueste, ...
```

Ese mensaje está escrito para un humano. Si aquí lo tiraras y lanzaras un `Error("400")`
genérico, todo ese trabajo se pierde exactamente en el punto donde iba a servir. Por eso se
propaga tal cual, y por eso el `.catch(() => ({}))`: si el backend se cayó de verdad y no
devolvió JSON, `datos` queda vacío y cae al mensaje genérico en lugar de reventar.

### Dos de esas cuatro todavía no tienen a quién llamar

`explicar` y `getHistory` apuntan a `/api/explain` y `/api/history`, que **no existen**: son
el material de la sesión 4. Las escribes hoy a propósito, y hoy no se usan las dos:

| función | endpoint | ¿existe hoy? |
|---|---|---|
| `getModel` | `/api/model` | sí, sesión 2 |
| `predecir` | `/api/predict` | sí, sesión 2 |
| `explicar` | `/api/explain` | **no**, sesión 4 |
| `getHistory` | `/api/history` | **no**, sesión 4 |

El formulario que vas a escribir va a pedir la explicación de todas formas, y no va a pasar
nada: el precio se muestra igual. Vuelvo a esto cuando lo veas ocurrir, porque es una de las
decisiones de diseño que más se llevan al reto.

Guarda. **La página ya no está en blanco.**

---

## 0:30 — El ensamblador del frontend (10 min)

Abre [frontend/src/main.jsx](../frontend/src/main.jsx). Es corto, y no lo vas a editar hoy ni
nunca.

```javascript
const modulos = import.meta.glob("./vistas/*.jsx", { eager: true });

const vistas = Object.values(modulos)
  .filter((m) => m.default && m.meta)
  .map((m) => ({ Componente: m.default, ...m.meta }))
  .sort((a, b) => a.orden - b.orden);
```

Compáralo con lo que ya conoces de `backend/app.py`:

| | backend | frontend |
|---|---|---|
| descubre | `AQUI.glob("s[0-9]_*.py")` | `import.meta.glob("./vistas/*.jsx")` |
| requisito | el módulo expone `bp` | el archivo exporta `default` y `meta` |
| resultado | rutas registradas solas | pestañas, ordenadas por `meta.orden` |

Es el **mismo patrón**, y por la misma razón: cuando llega el material de una sesión nueva son
**archivos nuevos**. Nunca hay que fusionar cambios sobre lo que ya escribiste.

Mira el encabezado de cualquier vista:

```javascript
export const meta = { titulo: "Predecir", orden: 2 };
```

Eso es todo lo que hace falta para que aparezca una pestaña. Agregar una vista en tu reto es
agregar un archivo con esas dos exportaciones — ni registrarla, ni tocar un router, ni
enterar a nadie.

Y nota dónde quedó tu tablero de la sesión 1: en `frontend/src/vistas/Tablero.jsx`, el mismo
código, con tres cambios. Ábrelo y compáralo con lo que tenías:

- gana `export const meta`
- importa de `"../api.js"` en vez de `"./api.js"` — bajó un nivel de carpeta
- soltó el `<div className="page">` y el `<header>`, que ahora son del ensamblador

**Una vista no sabe dónde vive.** No pinta el marco, no pinta el título, no sabe que hay
pestañas. Solo su contenido. Por eso se pudo mudar sin reescribirla.

Abre `http://TU-IP:3000`. Cuatro pestañas. Dos funcionan, dos son tu trabajo de hoy.

---

## 0:40 — El formulario que sale del contrato (40 min)

Abre [frontend/src/vistas/Predecir.jsx](../frontend/src/vistas/Predecir.jsx).

Aquí está la idea central de la sesión, y es la que más se lleva a tu reto:

> El formulario **no tiene una lista de campos escrita a mano.**
> Se construye con lo que dice `/api/model`.

Si escribieras los diez campos a mano, el día que tu modelo gane una feature tienes que
acordarte de venir aquí. Y no te vas a acordar. Lo que va a pasar es que el formulario
mandará nueve campos, el backend responderá `falta la feature 'X'`, y vas a perder media hora
buscándolo en el lugar equivocado.

### `TODO 6` — leer el contrato al montar

```javascript
  useEffect(() => {
    getModel()
      .then((c) => {
        setContrato(c);
        const iniciales = {};
        for (const f of c.features) {
          iniciales[f.name] = f.type === "num" ? f.median : f.allowed[0];
        }
        setValores(iniciales);
      })
      .catch((e) => setError(`No se pudo leer el contrato del modelo: ${e.message}`));
  }, []);
```

Los valores iniciales salen del contrato: la **mediana** si la feature es numérica, el primer
valor permitido si es categórica. El formulario abre con una casa plausible, no con diez
campos vacíos — y eso no lo decidiste tú, lo decidió el dataset.

### `TODO 7` — enviar

```javascript
  async function enviar(evento) {
    evento.preventDefault();
    if (enviando) return; // sin envios duplicados mientras hay uno en curso

    setEnviando(true);
    setError(null);
    setResultado(null);
    setExplicacion(null);
    setReferencia(null);

    try {
      const r = await predecir(valores);
      setResultado(r);

      // Las dos peticiones de contexto van DESPUES y por separado: si
      // cualquiera falla, el usuario se queda con su precio igual.
      explicar(valores, r.prediction)
        .then((e) => setExplicacion(e.explanation))
        .catch(() => setExplicacion(null));

      // Un precio solo no dice nada. Al lado del promedio de su colonia --que
      // es el mismo /api/stats de la sesion 1-- ya es una decision.
      getStats(valores.Neighborhood)
        .then((s) => setReferencia(s))
        .catch(() => setReferencia(null));
    } catch (e) {
      setError(e.message);
    } finally {
      setEnviando(false);
    }
  }
```

Fíjate en la última llamada: **`getStats` es de la sesión 1.** No hubo que agregar nada al
backend ni a la costura. Un precio solo no dice nada; el mismo precio al lado del promedio de
su colonia ya es una decisión:

> El promedio en **Blmngtn** es USD 194,871 sobre 17 casas vendidas — esta casa está **9%
> abajo**.

Eso es lo que significa que el módulo de la sesión 1 siga sirviendo: las piezas se combinan,
no se reemplazan.

Cuatro decisiones más, y las cuatro se notan cuando faltan:

- **`preventDefault()`.** Sin esto el navegador recarga la página y pierdes todo. Es el error
  número uno con formularios en React.
- **`if (enviando) return`.** Doble clic = dos predicciones registradas = tu historial
  mintiendo. El botón además se deshabilita, pero el guardia va en la lógica: deshabilitar un
  botón es cosmética, cualquiera puede mandar el submit con Enter.
- **Se limpia el resultado anterior.** Si no, mientras carga la nueva predicción el usuario
  está viendo el precio de la casa pasada. Un número viejo en pantalla es peor que ningún
  número.
- **Los `catch` del contexto no hacen nada.** Es deliberado, y hoy lo vas a ver funcionar de
  verdad: `/api/explain` **no existe todavía** —llega en la sesión 4— así que esa llamada va a
  fallar cada vez que pidas un precio. Y no pasa nada. El precio aparece, la referencia de la
  colonia aparece, y la explicación simplemente no está.

  Eso no es suerte. Si hubieras puesto ese `await` dentro del `try` de arriba, un endpoint que
  ni siquiera existe estaría borrando un precio perfectamente bueno.

  > **Lo secundario no tumba lo principal.** Escríbelo en tu reto antes de necesitarlo.

  Ábrelo en la consola del navegador después de estimar un precio: vas a ver el `404` de
  `/api/explain`, y la pantalla intacta.

### `TODO 8` — los campos

```javascript
          <div className="campos">
            {contrato.features.map((f) => (
              <label key={f.name} className="campo">
                <span className="etiqueta-campo">{f.name}</span>

                {f.type === "cat" ? (
                  <select
                    value={valores[f.name] ?? ""}
                    onChange={(e) =>
                      setValores({ ...valores, [f.name]: e.target.value })
                    }
                  >
                    {f.allowed.map((v) => (
                      <option key={v} value={v}>
                        {v}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type="number"
                    step="any"
                    value={valores[f.name] ?? ""}
                    onChange={(e) =>
                      setValores({ ...valores, [f.name]: e.target.value })
                    }
                  />
                )}

                {f.type === "num" && (
                  <span className="ayuda-campo">
                    entre {f.min.toLocaleString()} y {f.max.toLocaleString()}
                  </span>
                )}
              </label>
            ))}
          </div>
```

Un `.map` sobre `contrato.features`, y de ahí sale todo:

- `f.type === "cat"` → un `<select>` con `f.allowed`. **Es imposible escoger una colonia
  inválida**, porque las opciones son exactamente las que el modelo vio.
- `f.type === "num"` → un `<input type="number">` y debajo `entre f.min y f.max`. El rango se
  muestra pero **no se impone**: puedes escribir 9000 pies cuadrados. Vuelvo a esto al final.

Guarda y prueba. Deberías ver el formulario con diez campos y, al presionar **Estimar
precio**, el número grande con su explicación abajo.

Si algo falla, prueba primero con `curl` el mismo endpoint. Si `curl` funciona y el navegador
no, el problema es CORS o la URL — no tu lógica.

---

## 1:20 — La Model Card, que ya viene hecha (10 min)

Abre [frontend/src/vistas/ModelCard.jsx](../frontend/src/vistas/ModelCard.jsx) y la pestaña
**Model Card** en el navegador, lado a lado.

No hay nada que escribir aquí. El ejercicio es **leerla**, porque es la vista que más te va a
servir en el reto y casi nadie la abre por su cuenta.

Seis paneles, y cada uno lleva escrito a qué renglón de la rúbrica responde:

| Panel | Rúbrica |
|---|---|
| Qué modelo es | configura y entrena el modelo |
| Con cuántos datos | separa en entrenamiento, validación y prueba |
| Qué tan bien predice | selecciona medidas de desempeño adecuadas |
| Qué pesa en la predicción | interpreta los resultados del modelo |
| Modelos comparados | selecciona el modelo adecuado al problema |
| Experimentos de hiperparámetros | ajusta los hiperparámetros |

**Ni un solo valor está escrito a mano.** Todos salen de `/api/model`, que a su vez sale de
`metadata.json`, que a su vez lo escribió tu notebook. Busca en el código dónde está el
número `0.9024` que ves en pantalla. No está:

```javascript
              {metricas.map(([nombre, m]) => (
                <tr key={nombre}>
                  <td className="txt">{nombre}</td>
                  <td>{m.rmse.toLocaleString()}</td>
                  <td>{m.mae.toLocaleString()}</td>
                  <td>{m.r2}</td>
                </tr>
              ))}
```

### Los dos paneles vacíos son el encargo

**Modelos comparados** y **Experimentos de hiperparámetros** salen vacíos, con un mensaje que
dice qué llenar:

> Sin datos. En tu reto, llena `model_comparison` en `metadata.json` con los candidatos que
> probaste y esta tabla aparece sola.

Eso es deliberado. En este módulo entrenamos **un** modelo sin discutirlo, porque el tema es
otro. En tu reto vas a probar varios y vas a tener que justificar cuál elegiste — y cuando lo
hagas, no escribes frontend: escribes JSON.

```json
"model_comparison": [
  {"algorithm": "LogisticRegression", "f1": 0.81, "notas": "baseline"},
  {"algorithm": "RandomForest",       "f1": 0.89, "notas": "elegido"}
]
```

Esa página es la que vas a enseñar cuando te pidan justificar tu modelo.

---

## 1:30 — La prueba que importa (12 min)

Dijimos que el formulario sale del contrato. Vamos a comprobarlo, porque "sale del contrato"
es fácil de decir y fácil de creer sin que sea cierto.

**En la instancia** —y esta vez sí en la instancia, a propósito: es un experimento que vas a
deshacer y no quieres que llegue a tu repositorio— edita `artifacts/metadata.json`, busca la
entrada de `GrLivArea` y cambia su `median` a `3000` y su `max` a `3500`. Luego:

```bash
./setup/run restart
```

Recarga el navegador y mira el formulario. Sin haber tocado **una sola línea de JSX**:

- el campo `GrLivArea` ahora abre en 3000
- la ayuda debajo dice `entre 334 y 3500`

Ahora estima un precio con `GrLivArea` en 4000 y mira la respuesta:

```
⚠ 'GrLivArea' = 4000 esta fuera del rango visto al entrenar (334 a 3500);
  la prediccion es menos confiable
```

La validación que escribiste en la **sesión 2** también salía del contrato. Cambiaste un
archivo de datos y se movieron tres capas a la vez: el formulario, la ayuda y la validación.
Eso es lo que significa que algo esté derivado del contrato, y es exactamente lo que va a
hacer que tu modelo de clasificación entre en este mismo frontend sin reescribirlo.

**Deja `metadata.json` como estaba.** El comando más rápido, en la instancia:

```bash
git checkout -- artifacts/metadata.json
```

---

## 1:42 — Usarlo de verdad (10 min)

Deja de mirar el código. Abre `http://TU-IP:3000` en el teléfono, o pásale la dirección a
alguien del equipo de al lado.

Haz el recorrido completo, como si no lo hubieras escrito tú:

1. **Tablero.** ¿Qué colonia es la más cara? Fíltrala.
2. **Predecir.** Arma una casa de esa colonia y estima su precio. Compáralo con el promedio
   que te dice la propia pantalla.
3. **Predecir otra vez**, cambiando solo `OverallQual` de 5 a 8. Mira cuánto se mueve el
   precio — es el 58% de importancia que la Model Card te había anunciado.
4. **Model Card.** Enséñale a tu compañero con qué datos se entrenó y qué tan bien predice,
   sin abrir el notebook.

### Lo que hay que notar

Nadie escribió JSON. Nadie supo que existe un endpoint. Y aun así el recorrido contesta las
tres preguntas que un producto de datos tiene que contestar:

```
   ¿qué dicen los datos?        el tablero
   ¿qué predice el modelo?      el formulario
   ¿por qué debería creerle?    la Model Card
```

Eso es lo que entregas. Lo demás —el historial, la explicación en palabras, la base de datos
de verdad— son mejoras sobre algo que **ya funciona**, y llegan en la sesión 4.

### Antes de cerrar, un vistazo incómodo

Con el formulario abierto, pon `GrLivArea` en **9000** y estima.

Sale alrededor de **166,000** — *menos* que la casa de 2,600 pies que probaste antes.

No es un bug. Un Random Forest **no extrapola**: nunca vio una casa de 9000 pies, así que la
mete por las ramas que conoce y devuelve un promedio de casas que no se le parecen. Y lo hace
con la misma cara de confianza que cuando acierta.

Por eso existe ese aviso amarillo, y por eso la interfaz lo muestra en vez de tragárselo. Tu
modelo **siempre va a devolver algo**. Que devuelva algo no significa que sepa. En tu reto de
clasificación pasa igual: una probabilidad de 0.97 sobre un caso que no se parece a nada del
entrenamiento sigue siendo 0.97 en pantalla.

---

## 1:52 — Cierre (8 min)

Antes de guardar, corre las pruebas:

```bash
./setup/run test
```

Sigue siendo la de la sesión 2 —que el notebook y el servicio predicen el mismo número— y
tiene que seguir en verde: hoy no tocaste el backend, así que si se rompió, se rompió por algo
que no querías.

Guarda todo, **en tu computadora**:

```bash
git add -A
git commit -m "sesión 3: el producto tiene interfaz"
git push
```

Y en la instancia: `./setup/run sync && ./setup/run restart`.

Lo que tienes ahora:

```
   API                                        INTERFAZ
   /api/health   ¿está sano?      ← ses. 1
   /api/stats    cifras           ← ses. 1    Tablero
   /api/data     casas            ← ses. 1    Tablero
   /api/model    el contrato      ← ses. 2    Predecir · Model Card
   /api/predict  predice y avisa  ← ses. 2    Predecir
```

Cinco endpoints, tres vistas, y **ni una línea de backend escrita hoy.** La sesión entera fue
conectar lo que ya tenías con alguien que lo pueda usar.

### Las tres ideas que te llevas

1. **El formulario sale del contrato.** Cambia `metadata.json` y cambia la interfaz. Lo
   comprobaste, no te lo creíste.
2. **Lo secundario no tumba lo principal.** `/api/explain` no existe y el precio se muestra
   igual.
3. **Agregar una vista es agregar un archivo.** El ensamblador la encuentra sola.

Las tres se copian tal cual a tu reto.

### Lo que viene en la sesión 4

Tu producto no tiene memoria: cierra la pestaña y no queda rastro de lo que predijo. Y tus
datos siguen siendo un CSV dentro del repositorio, que no sobrevive a que alguien apague la
instancia y levante otra.

La sesión 4 arregla las dos, en ese orden:

```
   1. El servicio recuerda      cada predicción queda registrada, y se consulta
      y explica                 el número se traduce a una frase
                                  -> /api/history, /api/explain, pestaña Historial
                                  -> las dos funciones de api.js que hoy no tienen a quién llamar

   2. El origen es una base     el CSV se va a PostgreSQL, fuera de la máquina
      de datos de verdad          -> y ningún endpoint se entera
```

Fíjate en que el punto 1 **ya está preparado desde hoy**: escribiste `explicar` y `getHistory`
en `api.js`, y el formulario ya pide la explicación. Cuando el backend exista, aparece sola.

Los comentarios `ATAJO-P1` que has ido viendo en el código marcan exactamente dónde tomamos el
camino corto y qué lo reemplaza después.

---

## Si te quedaste atrás

**En tu computadora:**

```bash
./setup/run recuperar 3 --si
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
> ./setup/run recuperar 3 --si
> ```


Te deja con la sesión 3 terminada. Compara contra lo tuyo antes de descartarlo: lo que
escribiste a medias suele estar más cerca de lo que crees.
