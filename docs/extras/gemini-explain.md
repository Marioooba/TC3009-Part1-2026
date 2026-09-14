# Extra — Cambiar la plantilla por un modelo de lenguaje

En la sesión 3, `/api/explain` devuelve una frase armada por una plantilla determinista:

```python
return (
    f"El modelo estima {prediccion:,.0f} para esta casa. "
    f"Lo que mas pesa en esa estimacion es {detalle}."
)
```

Funciona, no cuesta nada, y siempre dice lo mismo ante la misma entrada. Pero se nota que es
una plantilla.

Este documento es para el que quiera cambiarla por un modelo de lenguaje real en su reto. No
es parte de la sesión y no hace falta para nada de lo que se evalúa.

---

## Lo que NO cambia

Antes que nada, el punto del ejercicio:

```
   el modelo DECIDE el numero
   esta funcion lo TRADUCE
   nunca lo cambia
```

Si cambias `redactar()` por una llamada a un LLM, **el contrato de `/api/explain` se queda
igual**: recibe `{input, prediction}` y devuelve `{explanation, source}`. El frontend no se
entera, `Predecir.jsx` no se toca, y si el LLM falla el usuario sigue viendo su precio —
porque la explicación ya se pedía por separado.

Toda la sesión estuvo construida para que este cambio fuera reemplazar una función. Vale la
pena ver que efectivamente lo es.

---

## El problema con Gemini institucional

El Gemini que te da el Tec es **la interfaz de chat**, no una API. No tiene llave que puedas
poner en un servidor, y no hay forma de llamarlo desde Flask.

Eso deja tres caminos.

### 1 · Usarlo como está: el prompt, a mano

El más barato y el que más gente subestima. Copias la predicción y el contrato al chat, y
usas la respuesta para **escribir mejor la plantilla**.

```
Tengo un modelo de regresión que estima el precio de una casa en Ames, Iowa.

Para esta casa:
  OverallQual: 5 (mediana del dataset: 6)
  GrLivArea: 1144 pies² (mediana: 1464)
  TotalBsmtSF: 1144 pies² (mediana: 991.5)

El modelo estimó 140,638 dólares. Las importancias del modelo son:
OverallQual 0.58, GrLivArea 0.13, TotalBsmtSF 0.076.

Escribe una explicación de dos frases para alguien que va a vender esta casa.
No inventes cifras que no te di. No digas que el modelo "cree" o "piensa".
```

Haz eso con cinco o seis casas distintas, mira qué tienen en común las respuestas buenas, y
llévalo a tu plantilla. Acabas con mejor redacción y **cero dependencias nuevas**.

En [docs/prompts/](../prompts/) hay más prompts de este estilo para el reto.

### 2 · Una llave de Google AI Studio

`ai.google.dev` da una llave gratuita para Gemini con un límite de peticiones por minuto que
alcanza de sobra para un demo. Es una cuenta personal, no institucional.

```python
import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def redactar(entrada, prediccion):
    contrato = s2_modelo.contrato
    prompt = construir_prompt(entrada, prediccion, contrato)
    try:
        r = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        return r.text.strip()
    except Exception:
        current_app.logger.exception("el LLM no respondio; se usa la plantilla")
        return redactar_plantilla(entrada, prediccion)
```

Tres cosas que **no** son opcionales:

- **La llave sale de una variable de entorno.** Nunca en el código, nunca en el repositorio.
  Si la subes a GitHub, GitHub la detecta, Google la revoca, y tienes razón para agradecerlo.
- **Siempre hay respaldo.** Si el LLM no contesta —y a veces no contesta— cae a la plantilla.
  Un servicio externo caído no puede tumbar tu endpoint.
- **Hay un timeout.** Sin él, una llamada colgada bloquea a Flask. En la sesión 3 esto no se
  nota porque no hay llamadas externas; en cuanto agregas una, se nota.

### 3 · Bedrock, desde la propia instancia

AWS Academy Learner Lab da acceso a Bedrock en algunas regiones. La ventaja sobre la opción 2
es que la instancia ya tiene credenciales por su `LabInstanceProfile`: no manejas llaves.

La desventaja es que el acceso a los modelos hay que habilitarlo en la consola, la
disponibilidad cambia por región, y se te va el crédito. Si vas por aquí, mide primero cuánto
cuesta una llamada.

---

## Lo que se rompe cuando metes un LLM

Vale la pena tenerlo escrito antes de decidir:

| | plantilla | LLM |
|---|---|---|
| misma entrada, misma salida | sí | no |
| se puede probar con un assert | sí | no directamente |
| tarda | microsegundos | 1–3 segundos |
| puede inventar una cifra | no | sí |
| cuesta | nada | por llamada |

Lo de "puede inventar una cifra" es el riesgo real. Un LLM al que le pasas la predicción
puede escribir un número distinto en la frase, y el usuario va a leer la frase. Si vas por
este camino, **verifica que el número de la predicción aparezca literalmente en el texto**
antes de devolverlo, y si no aparece, cae a la plantilla.

```python
if f"{prediccion:,.0f}" not in texto:
    return redactar_plantilla(entrada, prediccion)
```

Ese chequeo de tres líneas es la diferencia entre una explicación y una mentira bien escrita.

---

## Cómo lo evalúa tu reto

La rúbrica no pide un LLM. Pide que la solución tenga una interfaz y que los resultados se
interpreten. Una plantilla determinista bien redactada cumple eso perfectamente, y es más
fácil de defender que una llamada externa que a veces falla.

Si metes un LLM, que sea porque resuelve un problema que tienes — no por tenerlo.
