// La direccion del backend se deriva de donde se cargo esta pagina.
//
// No esta escrita a mano a proposito: la IP publica de la instancia EC2 cambia
// cada vez que el laboratorio la reinicia. Si aqui hubiera una IP literal, la
// aplicacion dejaria de funcionar en cada sesion nueva y el sintoma seria un
// error de red imposible de entender.
//
// Asi funciona igual en la instancia (IP publica) que en local (localhost),
// sin configurar nada.
//
// El puerto SI es distinto: el frontend vive en el 3000 y el backend en el
// 8080. Puertos distintos = origenes distintos = el navegador aplica CORS.
const API_BASE = `http://${window.location.hostname}:8080`;

// ---------------------------------------------------------------------------
// ESTADO DE ARRANQUE: lo que sigue esta por escribir.
//
// App.jsx importa de aqui, asi que hasta que termines este archivo el tablero
// no va a poder pedir datos. Cuando lo acabes, cobra vida de golpe.
// ---------------------------------------------------------------------------

// TODO sesion 1: la funcion get()
//
// Recibe una ruta y un objeto de parametros, arma la URL completa, hace la
// peticion y devuelve el JSON.
//
// Dos cosas que tiene que hacer bien:
//   - omitir los parametros vacios, para no mandar ?neighborhood= sin valor
//   - lanzar un error si la respuesta no viene con codigo 200, para que la
//     interfaz pueda mostrar el problema en lugar de quedarse en blanco

// TODO sesion 1: las tres funciones que consume App.jsx
//
//   getHealth()                      -> GET /api/health
//   getStats(neighborhood)           -> GET /api/stats
//   getData(neighborhood, limit)     -> GET /api/data
//
// Tienen que exportarse con esos nombres exactos: App.jsx ya las importa asi.
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