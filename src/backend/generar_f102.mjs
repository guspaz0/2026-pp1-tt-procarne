/**
 * Generador de PDF F102 usando pdfme (Node.js).
 *
 * Lee el template-certificado-operador.json, rellena los campos dinámicos
 * con los datos pasados por stdin (JSON), y escribe el PDF en stdout.
 *
 * Uso:
 *   echo '{"numero_operador":"100001",...}' | node generar_f102.mjs > out.pdf
 *
 * El backend FastAPI invoca este script como subprocess.
 */

import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { generate } from "@pdfme/generator";
import { rectangle, line, table, image, text } from "@pdfme/schemas";

const __dirname = dirname(fileURLToPath(import.meta.url));
const TEMPLATE_PATH = resolve(__dirname, "app/core/pdfme/template-certificado-operador.json");
const LOGOS_DIR = resolve(__dirname, "app/assets/logos");

// Mapeo: nombre del campo en el template -> archivo en app/static/logos/
const LOGO_FILES = {
  logo_registro_ope_carne: "logo_registro_ope_carne.png",
  logo_m_produccion: "logo_m_produccion.png",
  logo_procarne: "logo_procarne.png",
  logo_agricultura_ganaderia: "logo_agricultura_ganaderia.png",
};
//const staticPath = resolve(__dirname, "app/static/logos");

// --- Leer datos desde stdin ---
function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
  });
}

// --- Formatear fechas ---
function fmtFecha(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const year = d.getFullYear();
  return day + "/" + month + "/" + year;
}

// --- Cargar logos reales desde app/static/logos/ como data-URI ---
function cargarLogos() {
  const logos = {};
  for (const [campo, archivo] of Object.entries(LOGO_FILES)) {
    const path = resolve(LOGOS_DIR, archivo);
    const buf = readFileSync(path);
    logos[campo] = "data:image/png;base64," + buf.toString("base64");
  }
  return logos;
}

// --- Construir el input que pdfme mapea por "name" del template ---
function construirInput(datos, logos) {
  const actividades = datos.actividades ?? [];
  const filasAct = actividades.map((a) => [a[0], a[1]]);
  while (filasAct.length < 6) filasAct.push(["", ""]);

  const inscripciones = datos.inscripciones ?? [];
  const filasInsc = inscripciones.map((i) => [i[0], i[1]]);
  while (filasInsc.length < 3) filasInsc.push(["", ""]);

  return {
    // Campos de texto (mapeados por "name" en el template)
    operador_numero: datos.numero_operador ?? "",
    APELLIDO_Y_NOMBRE: datos.apellido_y_nombre ?? "",
    NOMBRE_ESTABLECIMIENO: datos.nombre_establecimiento ?? "",
    RAZON_SOCIAL: datos.razon_social ?? "",
    CUIT: datos.cuit ?? "",
    DOMICILIO: datos.domicilio ?? "",
    TIPO_CARNE_COMERCIALIZADA: datos.tipo_carne ?? "",
    Fecha_de_inscripcion_operador: fmtFecha(datos.fecha_inscripcion),
    Fecha_vencimiento_certificado: fmtFecha(datos.fecha_vencimiento),
    // Tablas
    tabla_actividades: filasAct,
    inscripcion_table: filasInsc,
    // Logos (data-URI ya incrustados en el template)
    ...logos,
  };
}

// --- Main ---
async function main() {
  const stdinData = await readStdin();
  const datos = JSON.parse(stdinData);

  const templateRaw = readFileSync(TEMPLATE_PATH, "utf-8");
  const template = JSON.parse(templateRaw);

  const logos = cargarLogos();
  const input = construirInput(datos, logos);

  // Generar PDF
  const pdfBytes = await generate({
    inputs: [input],
    template: {
      schemas: template.schemas,
      basePdf: template.basePdf,
    },
    plugins: {
      rectangle,
      line,
      table,
      image,
      text,
    },
  });

  // Escribir PDF en stdout (binario)
  process.stdout.write(Buffer.from(pdfBytes));
}

main().catch((err) => {
  process.stderr.write("Error generando PDF: " + err.message + "\n" + (err.stack || "") + "\n");
  process.exit(1);
});
