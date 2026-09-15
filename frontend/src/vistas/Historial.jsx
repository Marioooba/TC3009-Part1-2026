export const meta = { titulo: "Historial", orden: 3 };

import { useEffect, useState } from "react";
import { getHistory } from "../api.js";

const pesos = (n) =>
  new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);

const cuando = (iso) => new Date(iso).toLocaleString("es-MX");

export default function Historial() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getHistory(50).then(setDatos).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="estado error">{error}</div>;
  if (!datos) return <div className="estado">Cargando...</div>;

  return (
    <>
      <p className="subtitulo-vista">
        Lo que este modelo ha estado prediciendo. No es el dataset de
        entrenamiento: es el uso real del producto.
      </p>

      <div className="panel">
        <h2>Predicciones recientes</h2>
        <p className="subtitulo">{datos.count} registradas</p>

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
      </div>
    </>
  );
}
