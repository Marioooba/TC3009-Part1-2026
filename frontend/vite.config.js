import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// NO hay proxy hacia el backend, a proposito.
//
// Un proxy haria que el navegador viera un solo origen y CORS desaparecia del
// panorama. Queremos justo lo contrario: que el frontend (3000) y el backend
// (8080) sean dos origenes distintos, para que CORS sea visible y se pueda
// explicar con el problema delante.
//
// En produccion el problema no existe: un solo contenedor sirve las dos cosas.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,

    // host: true hace que Vite escuche en todas las interfaces (0.0.0.0).
    //
    // Por defecto Vite solo atiende a localhost, asi que desde la instancia
    // EC2 responderia unicamente a la propia maquina y tu navegador veria un
    // timeout. Sin esta linea, la aplicacion "corre" y nadie puede verla.
    host: true,

    // strictPort: si el 3000 esta ocupado, Vite FALLA en lugar de moverse solo.
    //
    // Si se moviera al 3001, el backend no reconoceria ese origen y el sintoma
    // no seria "cambio el puerto" sino un error de CORS en la consola, mucho
    // mas dificil de diagnosticar. Preferimos fallar fuerte y temprano.
    strictPort: true,
  },
});
