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

const COOKIE_ACCESS = "rocca_access_token";

/**
 * Valida el token de acceso contra InsForge.
 * Devuelve true si el token es válido, false si no.
 */
async function validarToken(token) {
  if (!token) return false;
  const insforgeUrl = process.env.INSFORGE_URL;
  if (!insforgeUrl) return false; // Sin config, rechazar.
  // Normaliza la base: INSFORGE_URL puede terminar en "/" (p. ej.
  // "https://x.insforge.app/") y concatenar "/api/..." daría doble barra
  // ("//api/...") → 404. Removemos la barra final antes de armar la URL.
  const base = insforgeUrl.replace(/\/+$/, "");
  try {
    const resp = await fetch(`${base}/api/auth/sessions/current`, {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!resp.ok) return false;
    const data = await resp.json();
    return !!data.user;
  } catch {
    return false;
  }
}

function fmtFecha(iso) {
  if (!iso) return "Sin vencimiento";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const year = d.getFullYear();
  return day + "/" + month + "/" + year;
}

// Texto no vacío para campos requeridos del template (pdfme rechaza "").
function t(v) {
  return v && String(v).trim() !== "" ? String(v) : "-";
}

export default async function handler(req, res) {
  if (req.method !== "GET") {
    res.status(405).json({ detail: "Método no permitido" });
    return;
  }

  // --- Autenticación: validar cookie de sesión ---
  const cookies = req.headers.cookie || "";
  const token = cookies
    .split(";")
    .map((c) => c.trim())
    .find((c) => c.startsWith(`${COOKIE_ACCESS}=`))
    ?.split("=")
    .slice(1)
    .join("=");

  if (!token) {
    res.status(401).json({ detail: "Authentication required" });
    return;
  }

  const usuarioValido = await validarToken(token);
  if (!usuarioValido) {
    res.status(401).json({ detail: "Sesión inválida o vencida" });
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
      operador_numero: t(datos.numero_operador),
      APELLIDO_Y_NOMBRE: t(datos.apellido_y_nombre),
      NOMBRE_ESTABLECIMIENO: t(datos.nombre_establecimiento),
      RAZON_SOCIAL: t(datos.razon_social),
      CUIT: t(datos.cuit),
      DOMICILIO: t(datos.domicilio),
      TIPO_CARNE_COMERCIALIZADA: t(datos.tipo_carne),
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
