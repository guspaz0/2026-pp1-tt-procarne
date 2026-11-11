/**
 * Vercel Serverless Function — Genera el Formulario F 102 en PDF.
 *
 * Ruta: GET /api/f102?id=:operadorId
 *
 * Usa @pdfme/generator (Node.js) para renderizar el template
 * template-certificado-operador.json con los datos del operador.
 *
 * El template y los logos están embebidos en f102_data.mjs para
 * que la función sea autocontenida (no depende del filesystem).
 *
 * Devuelve FileTangoInfo en JSON.
 */

import { generate } from "@pdfme/generator";
import { rectangle, line, table, image, text } from "@pdfme/schemas";
import { TEMPLATE_JSON, LOGOS } from "./f102_data.mjs";

function fmtFecha(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const year = d.getFullYear();
  return day + "/" + month + "/" + year;
}

export default async function handler(req, res) {
  if (req.method !== "GET") {
    res.status(405).json({ detail: "Método no permitido" });
    return;
  }

  // Extraer operador_id del query param: ?id=4
  const id = req.query.id;
  if (!id || isNaN(Number(id))) {
    res.status(400).json({ detail: `ID de operador inválido (query=${JSON.stringify(req.query)})` });
    return;
  }
  const operadorId = Number(id);

  try {
    // --- Datos mockeados (estáticos) + datos del operador ---
    const datos = {
      numero_operador: String(100000 + operadorId),
      apellido_y_nombre: "OLIVEIRA DANIEL ALBERTO",
      nombre_establecimiento: "LA NORITA",
      razon_social: "LA NORITA S.R.L.",
      cuit: "23-30917912-9",
      domicilio: "JOSE BENJAMIN ABALOS N. 4582, B. ALMIRANTE BROWN, S.D.E.",
      tipo_carne: "CARNICERIAS",
      fecha_inscripcion: "2025-03-10",
      fecha_vencimiento: "2026-03-10",
      actividades: [
        ["922210", "Carniceria Minorista"],
        ["463110", "Comercializacion de carnes y chacinados"],
      ],
      inscripciones: [
        ["PRINCIPAL", "10/03/2025"],
      ],
    };

    // --- Template (embebido) ---
    const template = JSON.parse(TEMPLATE_JSON);

    // --- Construir input para pdfme ---
    const filasAct = datos.actividades.map((a) => [a[0], a[1]]);
    while (filasAct.length < 6) filasAct.push(["", ""]);

    const filasInsc = datos.inscripciones.map((i) => [i[0], i[1]]);
    while (filasInsc.length < 3) filasInsc.push(["", ""]);

    const input = {
      operador_numero: datos.numero_operador,
      APELLIDO_Y_NOMBRE: datos.apellido_y_nombre,
      NOMBRE_ESTABLECIMIENO: datos.nombre_establecimiento,
      RAZON_SOCIAL: datos.razon_social,
      CUIT: datos.cuit,
      DOMICILIO: datos.domicilio,
      TIPO_CARNE_COMERCIALIZADA: datos.tipo_carne,
      Fecha_de_inscripcion_operador: fmtFecha(datos.fecha_inscripcion),
      Fecha_vencimiento_certificado: fmtFecha(datos.fecha_vencimiento),
      tabla_actividades: filasAct,
      inscripcion_table: filasInsc,
      ...LOGOS,
    };

    // --- Generar PDF ---
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

    // --- Responder con FileTangoInfo ---
    const pdfB64 = Buffer.from(pdfBytes).toString("base64");
    res.status(200).json({
      fileContents: pdfB64,
      contentType: "application/pdf",
      fileDownloadName: `F102-${100000 + operadorId}.pdf`,
      lastModified: null,
      entityTag: null,
      enableRangeProcessing: false,
    });
  } catch (err) {
    console.error("Error generando F102:", err);
    res.status(500).json({ detail: "Error generando PDF F102: " + err.message });
  }
}
