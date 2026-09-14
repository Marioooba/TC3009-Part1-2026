# TC3009 · Parte 1 — De un modelo a un producto

Módulo nivelador de la concentración de Inteligencia Artificial Avanzada y Ciencia de Datos.

Ya sabes entrenar modelos. Este módulo trata de lo otro: qué pasa entre un notebook que
predice bien y algo que otra persona puede usar. Cuatro sesiones de dos horas, construyendo
en vivo.

Lo que te llevas no es el producto de precios de casas. Es el **template que vas a
re-apuntar a tu reto**, que es un problema de clasificación.

---

## Cómo funciona esto

Tu laptop **no** corre la aplicación. La escribe.

```
   Tu laptop              GitHub              Tu instancia EC2
   ─────────────          ──────              ────────────────
   VS Code + git   ─push──▶  tu fork  ─pull──▶  Ubuntu Server
   sólo editar                                  Flask  :8080
                                                Vite   :3000
                                     ◀── terminal desde el navegador
                                         (Session Manager, sin SSH)
```

Da igual si usas Windows o Mac: el código corre en Ubuntu, igual para todos. Y no necesitas
instalar Python, ni Node, ni Docker en tu computadora.

**Vas a clonar este repositorio dos veces**, con papeles distintos:

| Dónde | Para qué | Con qué |
| ----- | -------- | ------- |
| Tu computadora | **editar** el código | VS Code |
| Tu instancia EC2 | **ejecutar** la aplicación | la terminal del navegador |

Nunca edites archivos en la instancia: lo que escribas ahí lo borra el siguiente
`./setup/run sync`. Y nunca intentes correr la aplicación en tu computadora: no tiene
Python ni Node instalados, a propósito.

---

## Antes de la primera sesión

**[docs/00-setup.md](docs/00-setup.md) es tarea previa.** Son 15 minutos: git, VS Code,
cuenta de GitHub, y hacer fork de este repositorio.

No instales nada más. En serio.

---

## Si te quedas atrás, no te quedes atrás

Pasa, y está previsto. No preguntes, no te disculpes, no intentes alcanzar tecleando más
rápido. Salta al último checkpoint y sigue: **[la red de seguridad](#si-algo-se-rompe-la-red-de-seguridad)**
te devuelve al estado correcto sin perder tu trabajo ni tu artefacto.

> No uses `git reset --hard s2` a mano. Ese tag vive en **tu** fork y se quedó fijo en el
> commit que existía cuando forkeaste: no se mueve aunque el curso publique correcciones.
> `recuperar` lee del curso, así que siempre te trae la versión buena.

---

## Las cuatro sesiones

| # | Tema | Qué construyes |
|---|------|----------------|
| 1 | **La máquina y el contrato** | Tu instancia Ubuntu, la API en Flask, el tablero corriendo. Y CORS |
| 2 | **La costura** | El modelo cruza la frontera: pipeline exportado, contrato, validación, paridad |
| 3 | **El producto** | El frontend: formulario derivado del contrato, Model Card. Cero backend |
| 4 | **Memoria y origen** | Historial, explicación, y el CSV se muda a una base de datos |

La sesión 2 es la más importante del módulo. Si vas a faltar a una, que no sea esa.

---

## Comandos de tu instancia

```bash
./setup/run start     # levanta la API y el tablero en segundo plano
./setup/run restart   # relánzalos con el código nuevo (después de un sync)
./setup/run stop      # detenlos
./setup/run status    # qué está corriendo y en qué puerto
./setup/run logs      # últimas líneas de los dos registros
./setup/run sync      # trae los cambios que empujaste desde tu laptop
./setup/run actualizar 2   # trae el material para empezar la sesión 2
./setup/run recuperar 1    # te repara: te deja como al cerrar la sesión 1
./setup/run url       # en qué dirección está tu tablero
./setup/run doctor    # revisa el entorno y dice qué falta
./setup/run test      # corre todas las pruebas
./setup/run test paridad   # solo una: notebook ↔ servicio
```

**La consola del navegador es una sola.** Por eso `start` deja los servidores en
segundo plano y te devuelve el prompt: con una consola alcanza para todo. Si necesitas
ver qué está pasando, `./setup/run logs`.

Y no hace falta activar el entorno virtual: el script llama a `.venv/bin/python`
directamente.

Cuando algo no cuadre, empieza por aquí:

```bash
./setup/run doctor
```

Verifica que la API respira:

```bash
curl http://localhost:8080/api/health
```

---

## Dos reglas que no son negociables

**`git push` al cerrar cada sesión.** Tu código vive en una máquina que puede perderse —un
reset del laboratorio, el presupuesto agotado—. GitHub es la única copia que sobrevive.

**Detener la instancia al terminar, nunca terminarla.** Es tu entorno de trabajo de las
cuatro sesiones. El laboratorio la reinicia sola en la siguiente clase, con una IP nueva —
por eso nada en el código apunta a una dirección fija.

---

## Cómo está organizado

```
backend/          la API en Flask
frontend/         el tablero en React + Vite
notebooks/        entrenamiento y exportación del modelo (sesión 2)
artifacts/        el modelo exportado y su contrato (sesión 2)
data/             train.csv del dataset House Prices
tests/            las pruebas: paridad del modelo, registro de predicciones
setup/            aprovisionamiento de la instancia
docs/             guías de sesión, contrato de API, material de apoyo
template-clasificacion/   lo que te llevas al reto
```

---

## Documentos que vas a usar

| Documento | Cuándo |
|---|---|
| [docs/00-setup.md](docs/00-setup.md) | Antes de la sesión 1 |
| [docs/api-contrato.md](docs/api-contrato.md) | Todo el tiempo. Es la referencia de la API |
| [docs/s1-guia.md](docs/s1-guia.md) | Sesión 1 — la máquina y el contrato |
| [docs/s2-guia.md](docs/s2-guia.md) | Sesión 2 — el modelo cruza la frontera |
| [docs/s3-guia.md](docs/s3-guia.md) | Sesión 3 — el producto (frontend) |
| [docs/s4-guia.md](docs/s4-guia.md) | Sesión 4 — memoria, palabras y un origen de verdad |
| [docs/extras/](docs/extras/) | Opcional, para el reto |

Cada sesión empieza trayendo su material:

```bash
./setup/run actualizar 3      # el número de la sesión que vas a empezar
```

Llegan archivos **nuevos**; lo que ya escribiste no se toca. Quién es dueño de qué está en
[setup/archivos-del-curso.txt](setup/archivos-del-curso.txt).

---

## Si algo se rompe: la red de seguridad

No importa qué tan atrás vayas, qué hayas borrado, ni desde cuándo no actualizas. **Un solo
comando te devuelve al estado correcto**, en tu computadora:

```bash
./setup/run recuperar 2 --si     # el número de la sesión que quieres tener terminada
git push --force
```

Y en la instancia: `./setup/run sync && ./setup/run restart`.

Tres cosas que ese comando garantiza:

| | |
|---|---|
| **No pierdes nada** | Todo lo que tenías queda en una rama `respaldo/<fecha>`. Si te arrepientes, `git reset --hard respaldo/...` y vuelves |
| **Conservas tu artefacto** | `artifacts/` es tuyo y se restaura. No tienes que volver a correr el notebook |
| **Se actualiza sola** | Si tu copia de `setup/` es vieja, trae la del curso y se relanza con ella |

### Si ni eso funciona

Si tu fork es tan viejo que `recuperar` ni existe, arráncalo con git puro — tres líneas que
funcionan siempre, desde cualquier estado:

```bash
git fetch https://github.com/vsosahdz/TC3009-Part1-2026.git main
git checkout FETCH_HEAD -- setup/
./setup/run recuperar 2 --si
```

La primera línea trae la herramienta al día; la tercera ya es la versión nueva.

---

## Una convención que vas a ver en el código

```python
# ATAJO-P1: el CSV se carga completo en memoria al arrancar.
#           Parte 2 -> base de datos, consultas, paginacion real.
```

Cada vez que simplificamos algo a propósito, queda marcado y dice a dónde lleva. No son
descuidos: son decisiones, y la Parte 2 es donde se abren.

```bash
grep -rn "ATAJO-P1" .
```

Esa lista es, casi literalmente, el temario del módulo siguiente.
