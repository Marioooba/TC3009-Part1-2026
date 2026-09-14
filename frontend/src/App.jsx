import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getData, getStats } from "./api.js";

const SERIE = "#2a78d6";
const SERIE_APAGADA = "#86b6ef";
const EJE = "#c3c2b7";
const LINEA = "#e1e0d9";
const TINTA_APAGADA = "#898781";

const pesos = (n) =>
  new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);

const miles = (n) => new Intl.NumberFormat("es-MX").format(n);

/** Tooltip compartido por las dos graficas. */
function TooltipPrecio({ active, payload, label, sufijo = "" }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="tooltip">
      <div className="t-titulo">
        {label}
        {sufijo}
      </div>
      <div className="t-linea">Precio medio: {pesos(d.mean_price)}</div>
      <div className="t-linea">{miles(d.count)} casas</div>
    </div>
  );
}

export default function App() {
  const [stats, setStats] = useState(null);
  const [filas, setFilas] = useState(null);
  const [colonia, setColonia] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  // Cada vez que cambia el filtro, se vuelve a preguntar al backend.
  // El filtrado ocurre en el servidor, no en el navegador: el frontend no
  // guarda una copia del dataset.
  useEffect(() => {
    let cancelado = false;
    setCargando(true);
    setError(null);

    Promise.all([getStats(colonia), getData(colonia, 20)])
      .then(([s, d]) => {
        if (cancelado) return;
        setStats(s);
        setFilas(d);
      })
      .catch((e) => !cancelado && setError(e.message))
      .finally(() => !cancelado && setCargando(false));

    return () => {
      cancelado = true;
    };
  }, [colonia]);

  if (error) {
    return (
      <div className="page">
        <div className="estado error">
          <p>No se pudo hablar con la API: {error}</p>
          <p>
            Revisa que el backend este corriendo en el puerto 8080 y que la
            consola del navegador no muestre un error de CORS.
          </p>
        </div>
      </div>
    );
  }

  if (cargando && !stats) {
    return (
      <div className="page">
        <div className="estado">Cargando datos...</div>
      </div>
    );
  }

  const colonias = stats.by_neighborhood.map((d) => d.neighborhood).sort();
  const alcance = stats.scope ? `la colonia ${stats.scope}` : "las 1,460 casas";

  return (
    <div className="page">
      <header>
        <h1>Tablero de precios de vivienda</h1>
        <p>Ames, Iowa &middot; {miles(stats.count)} registros en el alcance actual</p>
      </header>

      {/* Los filtros van en una sola fila, arriba de todo lo que afectan. */}
      <div className="filtros">
        <label htmlFor="colonia">Colonia</label>
        <select
          id="colonia"
          value={colonia}
          onChange={(e) => setColonia(e.target.value)}
        >
          <option value="">Todas las colonias</option>
          {colonias.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        {colonia && (
          <button onClick={() => setColonia("")}>Quitar filtro</button>
        )}
      </div>

      {/* Cifras de encabezado: son numeros, no una grafica. */}
      {stats.target ? (
        <div className="tarjetas">
          <div className="tarjeta">
            <div className="etiqueta">Casas</div>
            <div className="valor">{miles(stats.count)}</div>
          </div>
          <div className="tarjeta">
            <div className="etiqueta">Precio medio</div>
            <div className="valor">{pesos(stats.target.mean)}</div>
          </div>
          <div className="tarjeta">
            <div className="etiqueta">Mediana</div>
            <div className="valor">{pesos(stats.target.median)}</div>
          </div>
          <div className="tarjeta">
            <div className="etiqueta">Maximo</div>
            <div className="valor">{pesos(stats.target.max)}</div>
          </div>
        </div>
      ) : (
        <div className="panel vacio">
          No hay registros para {stats.scope}.
        </div>
      )}

      {/* Grafica 1: comparacion entre colonias.
          Se mantiene siempre completa; la seleccionada se resalta en lugar de
          esconder las demas. Filtrar no siempre significa ocultar. */}
      <div className="panel">
        <h2>Precio medio por colonia</h2>
        <p className="subtitulo">
          Las 25 colonias, ordenadas de mayor a menor.
          {stats.scope && ` ${stats.scope} aparece resaltada.`}
        </p>
        <ResponsiveContainer width="100%" height={520}>
          <BarChart
            data={stats.by_neighborhood}
            layout="vertical"
            margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
            barCategoryGap={3}
          >
            <CartesianGrid horizontal={false} stroke={LINEA} />
            <XAxis
              type="number"
              tickFormatter={(v) => `${Math.round(v / 1000)}k`}
              stroke={EJE}
              tick={{ fill: TINTA_APAGADA, fontSize: 12 }}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="neighborhood"
              width={86}
              interval={0}
              stroke={EJE}
              tick={{ fill: TINTA_APAGADA, fontSize: 12 }}
              tickLine={false}
            />
            <Tooltip
              content={<TooltipPrecio />}
              cursor={{ fill: "rgba(11,11,11,0.04)" }}
            />
            {/* Sin animacion de entrada: en un tablero es ruido, y ademas hace
                que la grafica dependa del tiempo para verse completa. */}
            <Bar
              dataKey="mean_price"
              radius={[0, 4, 4, 0]}
              isAnimationActive={false}
            >
              {stats.by_neighborhood.map((d) => (
                <Cell
                  key={d.neighborhood}
                  fill={
                    !stats.scope || stats.scope === d.neighborhood
                      ? SERIE
                      : SERIE_APAGADA
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Grafica 2: esta si refleja el filtro, porque la calidad dentro de una
          colonia es una pregunta con sentido. */}
      <div className="panel">
        <h2>Precio medio por calidad general</h2>
        <p className="subtitulo">
          Escala de 1 a 10, sobre {alcance}.
        </p>
        {stats.by_overall_qual.length === 0 ? (
          <div className="vacio">Sin datos para este filtro.</div>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart
              data={stats.by_overall_qual}
              margin={{ top: 4, right: 8, bottom: 4, left: 8 }}
              barCategoryGap={3}
              maxBarSize={52}
            >
              <CartesianGrid vertical={false} stroke={LINEA} />
              <XAxis
                dataKey="overall_qual"
                stroke={EJE}
                tick={{ fill: TINTA_APAGADA, fontSize: 12 }}
                tickLine={false}
              />
              <YAxis
                tickFormatter={(v) => `${Math.round(v / 1000)}k`}
                stroke={EJE}
                tick={{ fill: TINTA_APAGADA, fontSize: 12 }}
                tickLine={false}
              />
              <Tooltip
                content={<TooltipPrecio sufijo=" de calidad" />}
                cursor={{ fill: "rgba(11,11,11,0.04)" }}
              />
              <Bar
                dataKey="mean_price"
                fill={SERIE}
                radius={[4, 4, 0, 0]}
                isAnimationActive={false}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* La tabla es tambien la via de acceso accesible a lo que dicen las
          graficas: los mismos datos, en texto. */}
      <div className="panel">
        <h2>Registros</h2>
        <p className="subtitulo">
          {filas.count} de {miles(filas.total_matching)} casas que cumplen el
          filtro.
        </p>
        {filas.rows.length === 0 ? (
          <div className="vacio">Ninguna casa cumple este filtro.</div>
        ) : (
          <div className="scroll-x">
            <table>
              <thead>
                <tr>
                  <th className="txt">Id</th>
                  <th className="txt">Colonia</th>
                  <th>Superficie</th>
                  <th>Calidad</th>
                  <th>Año</th>
                  <th>Recámaras</th>
                  <th>Baños</th>
                  <th>Cochera</th>
                  <th className="txt">Cocina</th>
                  <th>Precio</th>
                </tr>
              </thead>
              <tbody>
                {filas.rows.map((f) => (
                  <tr key={f.Id}>
                    <td className="txt">{f.Id}</td>
                    <td className="txt">{f.Neighborhood}</td>
                    <td>{miles(f.GrLivArea)}</td>
                    <td>{f.OverallQual}</td>
                    <td>{f.YearBuilt}</td>
                    <td>{f.BedroomAbvGr}</td>
                    <td>{f.FullBath}</td>
                    <td>{f.GarageCars}</td>
                    <td className="txt">{f.KitchenQual}</td>
                    <td>{pesos(f.SalePrice)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
