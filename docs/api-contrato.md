# Contrato de la API

Este documento se escribe **antes** que el código. Define qué recibe y qué devuelve cada
endpoint. El backend implementa este contrato y el frontend lo consume; ninguno de los dos
adivina.

La regla del módulo: **si el contrato no está escrito, no se escribe código.**

Base de desarrollo: `http://localhost:8080` desde la propia instancia, o
`http://TU-IP-PUBLICA:8080` desde tu navegador.

> **Por qué el 8080 y no el 5000.** Porque tiene que estar abierto en el security group de la
> instancia, y 8080 es el puerto que ya abriste al crearla. Si cambias de puerto, cambia
> también la regla de entrada — si no, el paquete ni siquiera llega y el síntoma es un
> timeout, no un error.
>
> El frontend vive en el **3000**. Puertos distintos son orígenes distintos, y de ahí sale
> todo lo que vas a ver de CORS.

---

## Sesión 1

### `GET /api/health`

Estado del servicio. Es el primer endpoint que se escribe y el último que se consulta cuando
algo falla.

```json
{
  "status": "ok",
  "api_version": "1.0.0"
}
```

> Este endpoint **crece en la sesión 2**: cuando exista el artefacto del modelo, la respuesta
> incorpora `model_version`, `sklearn_version` y `artifact_hash`. Hoy no hay modelo, así que
> no hay nada que reportar sobre él.

---

### `GET /api/stats`

Agregados del dataset. Alimenta las gráficas del tablero.

**Parámetros**

| Nombre         | Tipo   | Obligatorio | Descripción                          |
| -------------- | ------ | ----------- | ------------------------------------ |
| `neighborhood` | string | no          | Acota los agregados a esa colonia    |

**Respuesta**

```json
{
  "count": 1460,
  "scope": null,
  "target": {
    "name": "SalePrice",
    "min": 34900,
    "mean": 180921.2,
    "median": 163000,
    "max": 755000
  },
  "by_neighborhood": [
    { "neighborhood": "NoRidge", "count": 41, "mean_price": 335295.3 }
  ],
  "by_overall_qual": [
    { "overall_qual": 5, "count": 397, "mean_price": 133523.3 }
  ]
}
```

`scope` es la colonia aplicada, o `null` si no hay filtro.

`by_neighborhood` viene ordenado por precio medio descendente.
`by_overall_qual` viene ordenado por calidad ascendente.

**Qué se filtra y qué no.** Cuando llega `neighborhood`, se acotan `count`, `target` y
`by_overall_qual`. **`by_neighborhood` se mantiene global a propósito**: es el eje de
comparación del tablero, y reducirlo a una sola barra lo dejaría sin sentido. El frontend
resalta la colonia seleccionada en lugar de esconder las demás.

Es una decisión de producto, no un descuido: filtrar no siempre significa ocultar.

Si la colonia no existe, la respuesta es `200` con `count: 0`, `target: null` y
`by_overall_qual: []`.

---

### `GET /api/data`

Registros individuales, con filtro opcional.

**Parámetros**

| Nombre         | Tipo   | Obligatorio | Por defecto | Descripción                        |
| -------------- | ------ | ----------- | ----------- | ---------------------------------- |
| `neighborhood` | string | no          | —           | Filtra por colonia (coincide exacto)|
| `limit`        | entero | no          | `20`        | Máximo de filas. Entre 1 y 200      |

**Respuesta**

```json
{
  "count": 20,
  "total_matching": 225,
  "rows": [
    {
      "Id": 1,
      "Neighborhood": "CollgCr",
      "GrLivArea": 1710,
      "OverallQual": 7,
      "YearBuilt": 2003,
      "TotalBsmtSF": 856,
      "GarageCars": 2,
      "FullBath": 2,
      "BedroomAbvGr": 3,
      "LotArea": 8450,
      "KitchenQual": "Gd",
      "SalePrice": 208500
    }
  ]
}
```

`count` es cuántas filas vienen en esta respuesta. `total_matching` es cuántas cumplen el
filtro en total. No son lo mismo, y la diferencia importa para paginar.

**Un filtro sin coincidencias no es un error.** Devuelve `200` con `rows: []` y
`total_matching: 0`. Un error es que algo salió mal; una búsqueda vacía es un resultado
legítimo.

Las columnas expuestas son las diez features que va a usar el modelo en la sesión 2, más
`Id` y `SalePrice`. No es casualidad: el tablero y el predictor hablan del mismo vocabulario.

---

## Sesión 2

### `GET /api/model`

El **contrato del modelo**: qué espera recibir y qué tan bien predice. Sale entero de
`metadata.json`, el archivo que el notebook exporta junto al pipeline.

Es el endpoint más importante del módulo. De él salen, sin escribir nada a mano: la
validación del backend, el formulario del frontend y la Model Card.

**Respuesta `200`**

```json
{
  "model_version": "1.0.0",
  "algorithm": "RandomForestRegressor(n_estimators=100)",
  "trained_at": "2026-09-10T04:51:08Z",
  "sklearn_version": "1.5.2",
  "artifact_hash": "6ff94a85591c",
  "target": "SalePrice",
  "target_transform": "log1p",
  "features": [
    { "name": "GrLivArea", "type": "num", "min": 334.0, "max": 5642.0, "median": 1464.0 },
    { "name": "Neighborhood", "type": "cat", "allowed": ["NAmes", "CollgCr", "..."] }
  ],
  "splits": { "train": 1022, "validation": 219, "test": 219 },
  "metrics": {
    "validation": { "rmse": 24841.6, "mae": 17109.1, "r2": 0.9018 },
    "test":       { "rmse": 27253.3, "mae": 17323.2, "r2": 0.9024 }
  },
  "feature_importances": { "OverallQual": 0.58, "GrLivArea": 0.132, "...": 0.0 },
  "model_comparison": [],
  "hyperparameter_experiments": []
}
```

Cada feature declara su tipo y su dominio: `min`/`max`/`median` si es numérica, `allowed` si
es categórica. Los dos últimos campos salen vacíos en este modelo y están en el contrato a
propósito, para que la Model Card los muestre en cuanto se llenen.

---

### `POST /api/predict`

**Cuerpo:** un objeto con **todas** las features de `/api/model`, con sus nombres exactos.

```json
{
  "GrLivArea": 1144, "OverallQual": 5, "YearBuilt": 1963, "TotalBsmtSF": 1144,
  "GarageCars": 1, "FullBath": 1, "BedroomAbvGr": 3, "LotArea": 9204,
  "Neighborhood": "NAmes", "KitchenQual": "TA"
}
```

**Respuesta `200`**

```json
{
  "prediction": 140637.5,
  "prediction_id": "680126c2-852f-43b4-a27d-a691a2258de7",
  "model_version": "1.0.0",
  "warnings": []
}
```

`prediction_id` identifica esa predicción para siempre: es la llave con la que el historial de
la sesión 3 la vuelve a encontrar.

**Un valor fuera de rango NO es un error.** Devuelve `200` con aviso:

```json
{
  "prediction": 166190.38,
  "warnings": ["'GrLivArea' = 9000 esta fuera del rango visto al entrenar (334 a 5642); la prediccion es menos confiable"]
}
```

El modelo puede predecir; lo que no puede es garantizar. Rechazarlo sería mentir en la otra
dirección.

**Respuesta `400`** — falta un campo, el tipo no corresponde, o la categoría no existe:

```json
{ "error": "'Neighborhood' no acepta el valor 'Polanco'. Valores validos: Blmngtn, Blueste, ..." }
```

El mensaje nombra **el campo** y, cuando aplica, los valores válidos. Está escrito para que
llegue tal cual a la pantalla del usuario.

**Respuesta `500`** — genérica a propósito. El detalle va al log del servidor, no al cliente.

---

## Sesión 3

### `GET /api/history`

Lo que la aplicación ha predicho. **No** es el dataset de entrenamiento: es el uso real del
producto.

**Parámetros**

| Nombre  | Tipo | Obligatorio | Por defecto | Notas                       |
| ------- | ---- | ----------- | ----------- | --------------------------- |
| `limit` | int  | no          | `50`        | Se acota entre 1 y 500      |

Un `limit` fuera de rango no es un error: se acota en silencio. El cliente nunca puede pedir
"todo".

**Respuesta `200`**

```json
{
  "count": 2,
  "rows": [
    {
      "prediction_id": "bfe04608-8142-4c00-86ce-481f6ab200ed",
      "created_at": "2026-09-14T07:57:55Z",
      "model_version": "1.0.0",
      "prediction": 89113.69,
      "input": { "GrLivArea": 900, "OverallQual": 3, "...": "..." }
    }
  ]
}
```

Más reciente primero. `input` trae la entrada **completa** con la que se hizo esa predicción:
es lo que permite, después, comparar lo que el modelo está viendo contra lo que vio al
entrenar.

`created_at` es siempre UTC en formato ISO-8601, puesto por el servidor. Nunca por el cliente.

---

### `POST /api/explain`

Traduce una predicción a una frase. **No la recalcula.**

**Cuerpo**

```json
{
  "input": { "GrLivArea": 1144, "OverallQual": 5, "...": "..." },
  "prediction": 140637.5
}
```

Recibir la predicción en lugar de volver a calcularla no es un ahorro: es lo que garantiza que
la explicación hable del mismo número que el usuario tiene en pantalla.

**Respuesta `200`**

```json
{
  "explanation": "El modelo estima 140,638 para esta casa. Lo que mas pesa en esa estimacion es OverallQual por debajo de lo habitual (5); ...",
  "source": "plantilla"
}
```

`source` dice quién redactó. Hoy siempre `"plantilla"`. Está en el contrato desde el principio
para que cambiarlo por un modelo de lenguaje —ver [extras/gemini-explain.md](extras/gemini-explain.md)—
no rompa a ningún consumidor.

**Respuesta `400`**

```json
{ "error": "se esperaba {input: {...}, prediction: numero}" }
```

---

### `GET /api/health` — lo que agrega esta sesión

`health` gana dos campos cuando algo va mal:

```json
{
  "status": "degradado",
  "modulos_con_falla": { "s3_producto": "no such table: predicciones" }
}
```

`status` es `"ok"` o `"degradado"`. Un módulo roto **no** tumba el chequeo de los demás: justo
cuando algo falla es cuando necesitas saber qué falla.

---

## Convenciones

- Todas las rutas viven bajo `/api/`. Lo que no empieza con `/api/` es frontend.
- Los nombres de campos van en inglés, igual que las columnas del dataset.
- Los códigos de estado significan lo de siempre: `200` salió bien, `400` el cliente mandó
  algo inválido, `500` el servidor falló. Un `500` nunca expone el detalle interno al cliente.
