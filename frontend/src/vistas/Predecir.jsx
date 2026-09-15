export const meta = { titulo: "Predecir", orden: 2 };

import { useEffect, useState } from "react";
import { explicar, getModel, getStats, predecir } from "../api.js";

const pesos = (n) =>
  new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);

export default function Predecir() {
  const [contrato, setContrato] = useState(null);
  const [valores, setValores] = useState({});
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [explicacion, setExplicacion] = useState(null);
  const [referencia, setReferencia] = useState(null);
  const [error, setError] = useState(null);

  // El formulario NO tiene una lista de campos escrita a mano: se construye
  // con lo que dice el contrato del modelo. Si el modelo gana una feature,
  // aqui aparece un campo. Si cambia el rango, cambia la ayuda.
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

  if (error && !contrato) {
    return <div className="estado error">{error}</div>;
  }
  if (!contrato) {
    return <div className="estado">Cargando el contrato del modelo...</div>;
  }

  return (
    <>
      <p className="subtitulo-vista">
        Modelo {contrato.model_version} &middot; entrenado el{" "}
        {contrato.trained_at.slice(0, 10)}
      </p>

      <div className="dos-columnas">
        <form className="panel" onSubmit={enviar}>
          <h2>Datos de la casa</h2>
          <p className="subtitulo">
            Diez campos. Son los que un vendedor conoce sin medir nada.
          </p>

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

          <button type="submit" className="primario" disabled={enviando}>
            {enviando ? "Consultando el modelo..." : "Estimar precio"}
          </button>
        </form>

        <div className="panel">
          <h2>Estimación</h2>

          {error && (
            <div className="aviso-error">
              <strong>No se pudo estimar.</strong>
              <p>{error}</p>
            </div>
          )}

          {!error && !resultado && (
            <p className="vacio">
              Llena el formulario y presiona <em>Estimar precio</em>.
            </p>
          )}

          {resultado && (
            <>
              <div className="precio">{pesos(resultado.prediction)}</div>

              {resultado.warnings?.length > 0 && (
                <div className="aviso-cuidado">
                  {resultado.warnings.map((w) => (
                    <p key={w}>{w}</p>
                  ))}
                </div>
              )}

              {referencia && (
                <p className="referencia">
                  El promedio en <strong>{referencia.scope}</strong> es{" "}
                  {pesos(referencia.target.mean)} sobre {referencia.count} casas
                  vendidas — esta casa está{" "}
                  <strong>
                    {Math.abs(
                      Math.round(
                        ((resultado.prediction - referencia.target.mean) /
                          referencia.target.mean) *
                          100,
                      ),
                    )}
                    %{" "}
                    {resultado.prediction >= referencia.target.mean
                      ? "arriba"
                      : "abajo"}
                  </strong>
                  .
                </p>
              )}

              {explicacion && <p className="explicacion">{explicacion}</p>}

              <dl className="ficha">
                <dt>modelo</dt>
                <dd>{resultado.model_version}</dd>
                <dt>id</dt>
                <dd className="mono">{resultado.prediction_id.slice(0, 8)}</dd>
              </dl>
            </>
          )}
        </div>
      </div>
    </>
  );
}
