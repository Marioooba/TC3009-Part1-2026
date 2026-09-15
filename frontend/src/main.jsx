import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import "./styles.css";

// Ensamblador de la interfaz. NO lo edites: cambia solo cuando cambia el curso.
//
// Cada vista vive en su propio archivo dentro de src/vistas/, y esta linea las
// descubre todas sin que haya que registrarlas a mano. Agregar una vista es
// agregar un archivo.
//
// Es el mismo patron que backend/app.py con los modulos de cada sesion, y por
// la misma razon: cuando llega el material de una sesion nueva son archivos
// NUEVOS, y nunca hay que fusionar cambios sobre lo que ya escribiste.
const modulos = import.meta.glob("./vistas/*.jsx", { eager: true });

const vistas = Object.values(modulos)
  .filter((m) => m.default && m.meta)
  .map((m) => ({ Componente: m.default, ...m.meta }))
  .sort((a, b) => a.orden - b.orden);

function App() {
  const [activa, setActiva] = useState(0);

  if (vistas.length === 0) {
    return (
      <div className="page">
        <div className="estado error">
          No hay ninguna vista en <code>src/vistas/</code>.
        </div>
      </div>
    );
  }

  const Actual = vistas[activa].Componente;

  return (
    <div className="page">
      <header>
        <h1>Precios de vivienda</h1>
        <p>Ames, Iowa &middot; un modelo puesto a trabajar</p>
      </header>

      <nav className="pestanas">
        {vistas.map((v, i) => (
          <button
            key={v.titulo}
            className={i === activa ? "activa" : ""}
            onClick={() => setActiva(i)}
          >
            {v.titulo}
          </button>
        ))}
      </nav>

      <Actual />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
