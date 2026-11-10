"""Generador del Certificado de Operador (PDF).

Reconstruye el diseño de ``template-certificado-operador.json`` (pdfme de Node)
usando la librería Python ``pdfme`` (aFelipeSP), posicionando cada elemento de
forma absoluta para replicar la maquetación del template original.

El template pdfme de Node usa:
- unidades en **milímetros** (página A4 = 210 x 297 mm),
- coordenadas ``y`` medidas **desde la base** (convención estándar de PDF).

La librería Python ``pdfme`` trabaja en **puntos** (A4 = 595.276 x 841.89 pt)
y mide ``y`` **desde la parte superior**. Por eso se aplica:

    factor = 72 / 25.4
    y_pdfme = altura_pagina - y_template - altura_elemento

Las imágenes del template (logos) están incrustadas como data-URI base64 PNG;
se reutilizan tal cual.
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

from pdfme import PDF
from pdfme.image import PDFImage

# ---------------------------------------------------------------------------
# Constantes de conversión
# ---------------------------------------------------------------------------
MM = 72 / 25.4  # puntos por milímetro
PAG_W_MM = 210.0
PAG_H_MM = 297.0
PAG_W_PT = PAG_W_MM * MM
PAG_H_PT = PAG_H_MM * MM

# Altura estimada (mm) de una línea de texto, usada para centrar verticalmente
# el contenido dentro del recuadro de cada campo.
LINE_MM = 4.0

# Color de fondo de las barras de sección (rojo semitransparente del template).
BARRA_BG = "#fc0202"

# Recuadro de la tabla de actividades (mm), extraído del template.
TABLA_ACT_X = 10.32
TABLA_ACT_Y = 86.94
TABLA_ACT_W = 188.38
TABLA_ACT_H = 48.28
TABLA_ACT_COLS = (47.0, 141.38)  # 24.85% / 75.14% del ancho

# Recuadro de la tabla de inscripción (mm). El template la deja auto (h=0);
# se asigna una altura fija para que quepa entre la sección de datos y la de
# actividades.
TABLA_INSC_X = 10.0
TABLA_INSC_Y = 189.0
TABLA_INSC_W = 190.0
TABLA_INSC_H = 38.0
TABLA_INSC_COLS = (38.0, 152.0)  # Tipo / Fecha de Inscripción

# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------


@dataclass
class CertificadoData:
    """Datos dinámicos del certificado."""

    numero_operador: str
    apellido_y_nombre: str = ""
    nombre_establecimiento: str = ""
    razon_social: str = ""
    cuit: str = ""
    domicilio: str = ""
    tipo_carne: str = ""
    fecha_inscripcion: datetime | None = None
    fecha_vencimiento: datetime | None = None
    inscripciones: list[tuple[str, str]] | None = None  # (tipo, fecha)
    actividades: list[tuple[str, str]] | None = None  # (codigo, descripcion)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------


def _hex_to_rgb(color: str | None) -> list[float]:
    """Convierte un color hex ``#rrggbb`` (con o sin alpha) a lista RGB 0-1."""
    if not color:
        return [0.0, 0.0, 0.0]
    c = color.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    c = c[:6]
    return [int(c[i : i + 2], 16) / 255 for i in (0, 2, 4)]


def _top_y(y_mm: float) -> float:
    """Convierte una ``y`` en mm desde la base a ``y`` en pt desde la parte superior."""
    return PAG_H_PT - (y_mm * MM)


def _fmt_fecha(fecha: datetime | None) -> str:
    if not fecha:
        return ""
    return fecha.strftime("%d/%m/%Y")


# ---------------------------------------------------------------------------
# Carga de logos desde el template
# ---------------------------------------------------------------------------


def _cargar_logos(template_path: Path) -> dict[str, PDFImage]:
    """Extrae las imágenes (logos) del template pdfme de Node.

    Devuelve un dict ``nombre -> PDFImage``.
    """
    data = json.loads(template_path.read_text(encoding="utf-8"))
    logos: dict[str, PDFImage] = {}
    for page in data.get("schemas", []):
        for el in page:
            if el.get("type") != "image":
                continue
            content = el.get("content", "")
            if not content.startswith("data:image/"):
                continue
            match = re.match(r"data:image/(\w+);base64,(.+)$", content, re.DOTALL)
            if not match:
                continue
            ext, b64 = match.group(1), match.group(2)
            raw = base64.b64decode(b64)
            name = el.get("name", "logo")
            logos[name] = PDFImage(BytesIO(raw), ext, name)
    return logos


# ---------------------------------------------------------------------------
# Generador
# ---------------------------------------------------------------------------


class CertificadoOperadorPDF:
    """Genera el PDF del certificado de operador."""

    def __init__(self, template_path: Path) -> None:
        self._logos = _cargar_logos(template_path)

    # -- primitivas de dibujo ------------------------------------------------

    def _texto(
        self,
        pdf: PDF,
        x_mm: float,
        y_mm: float,
        w_mm: float,
        h_mm: float,
        content: str,
        size: float = 11,
        color: str = "#000000",
        align: str = "left",
    ) -> None:
        """Dibuja un texto posicionado absolutamente, centrado verticalmente."""
        if content is None:
            content = ""
        if not content:
            return
        align_map = {"left": "l", "center": "c", "right": "r"}
        pdf._text(
            content,
            x=x_mm * MM,
            y=_top_y(y_mm + max(0.0, (h_mm - LINE_MM) / 2)),
            width=w_mm * MM,
            height=h_mm * MM,
            text_align=align_map.get(align, "l"),
            line_height=1.0,
            move="none",
        )

    def _rect(
        self,
        pdf: PDF,
        x_mm: float,
        y_mm: float,
        w_mm: float,
        h_mm: float,
        fill: str | None = None,
        border: str | None = None,
        border_width: float = 0.0,
    ) -> None:
        """Dibuja un rectángulo posicionado absolutamente."""
        content = {
            "x": x_mm * MM,
            "y": _top_y(y_mm),
            "width": w_mm * MM,
            "height": h_mm * MM,
        }
        if fill:
            content["fill"] = _hex_to_rgb(fill)
        if border and border_width:
            content["border"] = {
                "width": border_width * MM,
                "color": _hex_to_rgb(border),
            }
        pdf._content(content, move="none")

    def _linea(
        self,
        pdf: PDF,
        x_mm: float,
        y_mm: float,
        w_mm: float,
        color: str = "#000000",
        width: float = 0.4,
    ) -> None:
        """Dibuja una línea horizontal posicionada absolutamente."""
        pdf._content(
            {
                "x": x_mm * MM,
                "y": _top_y(y_mm),
                "width": w_mm * MM,
                "height": 0,
                "line": {"width": width * MM, "color": _hex_to_rgb(color)},
            },
            move="none",
        )

    def _imagen(
        self,
        pdf: PDF,
        logo: PDFImage | None,
        x_mm: float,
        y_mm: float,
        w_mm: float,
        h_mm: float,
    ) -> None:
        if logo is None:
            return
        pdf.add_image(
            logo,
            x=x_mm * MM,
            y=_top_y(y_mm),
            width=w_mm * MM,
            height=h_mm * MM,
            move="none",
        )

    def _tabla(
        self,
        pdf: PDF,
        x_mm: float,
        y_mm: float,
        w_mm: float,
        h_mm: float,
        cols: tuple[float, float],
        head: list[str],
        rows: list[list[str]],
    ) -> None:
        """Dibuja una tabla posicionada absolutamente (cabecera + filas)."""
        content: list = []
        content.append(
            [
                {
                    ".": c,
                    "style": {
                        "f": "Helvetica",
                        "s": 10,
                        "c": [0.0, 0.0, 0.0],
                        "bg": _hex_to_rgb(BARRA_BG),
                        "align": "l",
                    },
                }
                for c in head
            ]
        )
        for fila in rows:
            content.append(
                [
                    {
                        ".": c,
                        "style": {
                            "f": "Helvetica",
                            "s": 10,
                            "c": [0.0, 0.0, 0.0],
                            "align": "l",
                        },
                    }
                    for c in fila
                ]
            )
        pdf._table(
            content,
            x=x_mm * MM,
            y=_top_y(y_mm),
            width=w_mm * MM,
            height=h_mm * MM,
            widths=[cols[0] * MM, cols[1] * MM],
            borders=[
                {"width": 0.4 * MM, "color": _hex_to_rgb("#000000")},
            ],
            move="none",
        )

    # -- generación ----------------------------------------------------------

    def generar(self, data: CertificadoData) -> bytes:
        """Genera el PDF y devuelve los bytes."""
        pdf = PDF(page_size=(PAG_W_PT, PAG_H_PT), margin=0)
        pdf.add_page()

        # Marco exterior
        self._rect(
            pdf, 4.09, 4.84, 200.29, 232.57,
            border="#f90000", border_width=3.6,
        )

        # --- Encabezado ---
        self._imagen(pdf, self._logos.get("logo_m_produccion"), 27.26, 14.23, 20.64, 19.84)
        self._imagen(pdf, self._logos.get("logo_registro_ope_carne"), 74.12, 28.24, 9.16, 11.99)

        self._rect(pdf, 90, 13, 24, 9, fill="#000000")
        self._texto(pdf, 90, 14.5, 24, 6, "F 102", size=10, color="#ffffff", align="center")

        self._rect(pdf, 145.5, 7.93, 56.09, 8.47, fill="#000000")
        self._texto(
            pdf, 145.5, 9.43, 55.83, 6.09, "CERTIFICADO DE OPERADOR",
            size=10, color="#ffffff", align="center",
        )

        self._texto(
            pdf, 20.73, 35.48, 33.07, 10.58,
            "Ministerio de Producción,\nRecursos Naturales,\nF. y S.",
            size=7.5, align="center",
        )
        self._texto(
            pdf, 84.92, 29.51, 41.27, 11.11,
            "Registro Provincial de\nOPERADORES DE CARNE",
            size=10, align="left",
        )
        self._texto(pdf, 147.04, 30.97, 51.06, 3.97, "INSCRIPTO", size=7, align="center")
        self._texto(pdf, 143.14, 35.68, 8, 4, "Nº", size=7, align="left")
        self._texto(pdf, 142.27, 35.71, 55.83, 3.97, data.numero_operador, size=7, align="left")

        # --- Datos del Operador ---
        self._rect(pdf, 10, 54, 190, 6, fill=BARRA_BG)
        self._texto(pdf, 11, 54.53, 80, 6, "Datos del Operador", size=11, align="left")

        self._texto(pdf, 12, 60.62, 34.13, 5.82, "Apellido y Nombre", size=11, align="left")
        self._texto(pdf, 47.81, 60.69, 149.75, 5.82, data.apellido_y_nombre, size=11, align="left")
        self._linea(pdf, 11.64, 66.43, 186)

        self._texto(pdf, 12.26, 66.92, 55.83, 6.35, "Nombre del establecimiento", size=11, align="left")
        self._texto(pdf, 63.42, 66.97, 134.41, 6.09, data.nombre_establecimiento, size=11, align="left")
        self._linea(pdf, 11.85, 72.99, 186.41)

        self._texto(pdf, 12.27, 73.2, 25.93, 6.35, "Razon Social", size=11, align="left")
        self._texto(pdf, 35.71, 73.53, 93.13, 5.56, data.razon_social, size=11, align="left")
        self._texto(pdf, 130.98, 72.94, 13.49, 6.09, "C.U.I.T.", size=11, align="left")
        self._texto(pdf, 144.31, 73.28, 54.24, 5.82, data.cuit, size=11, align="left")
        self._linea(pdf, 11.81, 79.28, 186)

        # --- Tabla de actividades ---
        actividades = data.actividades or []
        filas_act = [[c, d] for c, d in actividades[:6]]
        while len(filas_act) < 6:
            filas_act.append(["", ""])
        self._tabla(
            pdf, TABLA_ACT_X, TABLA_ACT_Y, TABLA_ACT_W, TABLA_ACT_H,
            TABLA_ACT_COLS,
            ["Código de la Actividad", "Descripcion de la Actividad"],
            filas_act,
        )

        # --- Fecha de inscripción / vencimiento ---
        self._rect(pdf, 9.74, 148.25, 93.93, 6.09, fill=BARRA_BG)
        self._texto(
            pdf, 10.74, 148.25, 76.73, 6.09,
            "Fecha de Inscripción como operador", size=11, align="left",
        )
        self._texto(
            pdf, 11.61, 154.94, 91.55, 6.88,
            _fmt_fecha(data.fecha_inscripcion), size=7, align="left",
        )

        self._rect(pdf, 105.47, 148.47, 92.87, 6.09, fill=BARRA_BG)
        self._texto(
            pdf, 109.11, 148.73, 85.46, 6.09,
            "Fecha de vencimiento del Presente Certificado", size=11, align="left",
        )
        self._texto(
            pdf, 107.53, 154.93, 90.75, 6.61,
            _fmt_fecha(data.fecha_vencimiento), size=11, align="left",
        )

        # --- Datos de los Establecimientos ---
        self._rect(pdf, 10, 164, 190, 6, fill=BARRA_BG)
        self._texto(pdf, 11, 164, 100, 6, "Datos de los Establecimientos", size=11, align="left")

        self._texto(pdf, 12.26, 170.35, 23.81, 5.29, "Domicilio", size=11, align="left")
        self._texto(pdf, 35.11, 170.41, 163.25, 5.56, data.domicilio, size=11, align="left")
        self._linea(pdf, 11.76, 162.05, 186)

        self._texto(pdf, 12.47, 176.91, 53.71, 5.29, "Tipo de Carne Comercializada", size=11, align="left")
        self._texto(pdf, 65.53, 176.18, 132.03, 6.35, data.tipo_carne, size=11, align="left")
        self._linea(pdf, 12.45, 182.57, 186)

        # --- Tabla de inscripción ---
        inscripciones = data.inscripciones or []
        filas_insc = [[t, f] for t, f in inscripciones[:6]]
        while len(filas_insc) < 6:
            filas_insc.append(["", ""])
        self._tabla(
            pdf, TABLA_INSC_X, TABLA_INSC_Y, TABLA_INSC_W, TABLA_INSC_H,
            TABLA_INSC_COLS,
            ["Tipo", "Fecha de Inscripción"],
            filas_insc,
        )

        # --- Pie: logos + firma ---
        self._imagen(pdf, self._logos.get("logo_procarne"), 17.41, 197.26, 30.43, 28.84)
        self._imagen(pdf, self._logos.get("logo_agricultura_ganaderia"), 157.59, 196.94, 30.43, 28.84)
        self._linea(pdf, 70.3, 227.29, 68.53, width=0.2)
        self._texto(
            pdf, 81.04, 227.89, 50.8, 3.97,
            "Firma y Sello de la Autoridad competente", size=7, align="left",
        )

        out = BytesIO()
        pdf.output(out)
        return out.getvalue()


# ---------------------------------------------------------------------------
# Construcción de datos desde el servicio
# ---------------------------------------------------------------------------


def construir_certificado_data(
    servicio,
    operador,
    habilitaciones: list,
    inscripciones: list,
) -> CertificadoData:
    """Construye ``CertificadoData`` a partir de los objetos de dominio.

    Reglas de mapeo:
    - ``numero_operador``: el id del operador.
    - ``fecha_inscripcion``: la inscripción PRINCIPAL (o la primera).
    - ``fecha_vencimiento``: inscripción + 1 año (vencimiento del certificado).
    - ``actividades``: las habilitaciones (código = actividad, descripción = actividad).
    - ``tipo_carne``: la categoría del operador.
    """
    insc_principal = next(
        (i for i in inscripciones if getattr(i, "tipo", "") == "PRINCIPAL"),
        inscripciones[0] if inscripciones else None,
    )
    fecha_inscripcion = getattr(insc_principal, "fecha_inscripcion", None) if insc_principal else None
    fecha_vencimiento = (
        fecha_inscripcion + timedelta(days=365) if fecha_inscripcion else None
    )

    actividades = [
        (getattr(h, "actividad", ""), getattr(h, "actividad", ""))
        for h in habilitaciones
    ]
    inscripciones_pairs = [
        (getattr(i, "tipo", ""), _fmt_fecha(getattr(i, "fecha_inscripcion", None)))
        for i in inscripciones
    ]

    return CertificadoData(
        numero_operador=str(getattr(operador, "id", "")),
        apellido_y_nombre=getattr(operador, "razon_social", "") or "",
        nombre_establecimiento=getattr(operador, "razon_social", "") or "",
        razon_social=getattr(operador, "razon_social", "") or "",
        cuit=getattr(operador, "cuit", "") or "",
        domicilio=getattr(operador, "domicilio", "") or "",
        tipo_carne=getattr(operador, "categoria", "") or "",
        fecha_inscripcion=fecha_inscripcion,
        fecha_vencimiento=fecha_vencimiento,
        inscripciones=inscripciones_pairs,
        actividades=actividades,
    )
