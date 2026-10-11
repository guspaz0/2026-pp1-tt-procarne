# Modelos de Remitos Electrónicos Cárnicos

> Fuente: [AFIP — Modelos de Remitos Electrónicos Cárnicos 1.2](https://www.afip.gob.ar/actividadesagropecuarias/documentos/modelosRemitoElectrCarnicos-1-2.pdf)
> (PDF original: [`docs/modelosRemitoElectrCarnicos-1-2.pdf`](./modelosRemitoElectrCarnicos-1-2.pdf))

El documento describe los modelos de **Remito Electrónico Cárnico** según el caso de remisión de la mercadería. Todos los modelos comparten la misma estructura de sectores (A a F) y el pie: *"Documento no válido como factura"*.

## Índice de casos

| Caso | Descripción |
|------|-------------|
| 01 | Remisión de mercadería propia desde depósitos propios |
| 02 | Remisión de mercadería propia desde depósitos de terceros |
| 03 | Remisión de mercadería de terceros desde depósitos propios del emisor |
| 04 | Remisión de mercadería propia desde depósitos propios — Reparto |
| 05 | Remisión de mercadería propia desde depósitos de terceros — Reparto |
| 06 | Remisión de mercadería de terceros desde depósitos propios del emisor — Reparto |
| 07 | Entrega de mercadería en planta/depósito |

---

## CASO 01 — Remisión de mercadería propia desde depósitos propios

**Remito Electrónico Cárnico 01** — Remisión de mercadería propia desde depósitos propios

- `"Código del Remito Electrónico"`
- `"Documento no válido como factura"`
- (A1) nnnn - nnnnnnn
- (A2) Hoja nn de mmm
- (A3) Emisión
- (A4) Vencimiento

### ORIGEN DEL TRASLADO — TITULAR – DEPOSITARIO – EMISOR
- (B1) Razón Social
- (B2) CUIT
- (B3) Domicilio origen del traslado

### DESTINO DEL TRASLADO — DESTINATARIO
- (D1) Razón Social
- (D2) CUIT
- (D3) Domicilio destino del traslado

### TRANSPORTISTA — DATOS DEL TRANSPORTISTA
- (E1) Razón Social
- (E2) CUIT
- (E3) Domicilio fiscal
- (E4) Apellido y nombre del chofer
- (E5) Número Doc.
- (E6) Dominio del Vehículo

### DETALLE DE LA MERCADERÍA TRANSPORTADA
- (F1) Código AFIP
- (F2) Descripción
- (F3) Unidades / Kilogramos
- (F4) Firma
- (F5) Son nn hojas
- `"N° de Tropa"`

---

## CASO 02 — Remisión de mercadería propia desde depósitos de terceros

**Remito Electrónico Cárnico 02** — Remisión de mercadería propia desde depósitos de terceros

- `"Código del Remito Electrónico"`
- `"Documento no válido como factura"`
- (A1) nnnn - nnnnnnn
- (A2) Hoja nn de mmm
- (A3) Emisión
- (A4) Vencimiento

### ORIGEN DEL TRASLADO — TITULAR – EMISOR
- (B1) Razón Social
- (B2) CUIT

### DEPOSITARIO – AUTORIZANTE
- (C1) Razón Social
- (C2) CUIT
- (C3) Domicilio origen del traslado

### DESTINO DEL TRASLADO — DESTINATARIO
- (D1) Razón Social
- (D2) CUIT
- (D3) Domicilio destino del traslado

### TRANSPORTISTA — DATOS DEL TRANSPORTISTA
- (E1) Razón Social
- (E2) CUIT
- (E3) Domicilio fiscal
- (E4) Apellido y nombre del chofer
- (E5) Número Doc.
- (E6) Dominio del Vehículo

### DETALLE DE LA MERCADERÍA TRANSPORTADA
- (F1) Código AFIP
- (F2) Descripción
- (F3) Unidades / Kilogramos
- (F4) Firma
- (F5) Son nn hojas
- `"N° de Tropa"`

---

## CASO 03 — Remisión de mercadería de terceros desde depósitos propios del emisor

**Remito Electrónico Cárnico 03** — Remisión de mercadería de terceros desde depósitos propios del emisor

- `"Código del Remito Electrónico"`
- `"Documento no válido como factura"`
- (A1) nnnn - (8) nnnnnnn
- (A2) Hoja nn de mmm
- (A3) Emisión
- (A4) Vencimiento

### ORIGEN DEL TRASLADO — TITULAR – AUTORIZANTE
- (B1) Razón Social
- (B2) CUIT

### DEPOSITARIO – EMISOR
- (C1) Razón Social
- (C2) CUIT
- (C3) Domicilio origen del traslado

### DESTINO DEL TRASLADO — DATOS DEL DESTINATARIO
- (D1) Razón Social
- (D2) CUIT
- (D3) Domicilio destino del traslado

### TRANSPORTISTA — DATOS DEL TRANSPORTISTA
- (E1) Razón Social
- (E2) CUIT
- (E3) Domicilio fiscal
- (E4) Apellido y nombre del chofer
- (E5) Número Doc.
- (E6) Dominio del Vehículo

### DETALLE DE LA MERCADERÍA TRANSPORTADA
- (F1) Código AFIP
- (F2) Descripción
- (F3) Unidades / Kilogramos
- (F4) Firma
- (F5) Son nn hojas
- `"N° de Tropa"`

---

## CASO 04 — Remisión de mercadería propia desde depósitos propios (REPARTO)

**Remito Electrónico Cárnico 04** — Remisión de mercadería propia desde depósitos propios

- `"Código del Remito Electrónico"`
- `"Documento no válido como factura"`
- (A1) nnnn - nnnnnnn
- (A2) Hoja nn de mmm
- (A3) Emisión
- (A4) Vencimiento

### ORIGEN DEL TRASLADO — TITULAR – DEPOSITARIO – EMISOR
- (B1) Razón Social
- (B2) CUIT
- (B3) Domicilio origen del traslado

### REMITO DE REPARTO DE MERCADERÍA

### TRANSPORTISTA — DATOS DEL TRANSPORTISTA
- (E1) Razón Social
- (E2) CUIT
- (E3) Domicilio fiscal
- (E4) Apellido y nombre del chofer
- (E5) Número Doc.
- (E6) Dominio del Vehículo

### DETALLE DE LA MERCADERÍA TRANSPORTADA
- (F1) Código AFIP
- (F2) Descripción
- (F3) Unidades / Kilogramos
- (F4) Firma
- (F5) Son nn hojas
- `"N° de Tropa"`

---

## CASO 05 — Remisión de mercadería propia desde depósitos de terceros (REPARTO)

**Remito Electrónico Cárnico 05** — Remisión de mercadería propia desde depósitos de terceros

- `"Código del Remito Electrónico"`
- `"Documento no válido como factura"`
- (A1) nnnn - nnnnnnn
- (A2) Hoja nn de mmm
- (A3) Emisión
- (A4) Vencimiento

### ORIGEN DEL TRASLADO — TITULAR – EMISOR
- (B1) Razón Social
- (B2) CUIT

### DEPOSITARIO – AUTORIZANTE
- (C1) Razón Social
- (C2) CUIT
- (C3) Domicilio origen del traslado

### REMITO DE REPARTO DE MERCADERÍA

### TRANSPORTISTA — DATOS DEL TRANSPORTISTA
- (E1) Razón Social
- (E2) CUIT
- (E3) Domicilio fiscal
- (E4) Apellido y nombre del chofer
- (E5) Número Doc.
- (E6) Dominio del Vehículo

### DETALLE DE LA MERCADERÍA TRANSPORTADA
- (F1) Código AFIP
- (F2) Descripción
- (F3) Unidades / Kilogramos
- (F4) Firma
- (F5) Son nn hojas
- `"N° de Tropa"`

---

## CASO 06 — Remisión de mercadería de terceros desde depósitos propios del emisor (REPARTO)

**Remito Electrónico Cárnico 06** — Remisión de mercadería de terceros desde depósitos propios del emisor

- `"Código del Remito Electrónico"`
- `"Documento no válido como factura"`
- (A1) nnnn - (8) nnnnnnn
- (A2) Hoja nn de mmm
- (A3) Emisión
- (A4) Vencimiento

### ORIGEN DEL TRASLADO — TITULAR – AUTORIZANTE
- (B1) Razón Social
- (B2) CUIT

### DEPOSITARIO – EMISOR
- (C1) Razón Social
- (C2) CUIT
- (C3) Domicilio origen del traslado

### REMITO DE REPARTO DE MERCADERÍA

### TRANSPORTISTA — DATOS DEL TRANSPORTISTA
- (E1) Razón Social
- (E2) CUIT
- (E3) Domicilio fiscal
- (E4) Apellido y nombre del chofer
- (E5) Número Doc.
- (E6) Dominio del Vehículo

### DETALLE DE LA MERCADERÍA TRANSPORTADA
- (F1) Código AFIP
- (F2) Descripción
- (F3) Unidades / Kilogramos
- (F4) Firma
- (F5) Son nn hojas
- `"N° de Tropa"`

---

## CASO 07 — Entrega de mercadería en planta/depósito

**Remito Electrónico Cárnico 07** — Entrega de mercadería en planta/depósito

- `"Código del Remito Electrónico"`
- `"Documento no válido como factura"`
- (A1) nnnn - nnnnnnn
- (A2) Hoja nn de mmm
- (A3) Emisión
- (A4) Vencimiento

### ORIGEN DEL TRASLADO — TITULAR – DEPOSITARIO – EMISOR
- (B1) Razón Social
- (B2) CUIT
- (B3) Domicilio origen del traslado

### DESTINO DEL TRASLADO — DESTINATARIO
- (D1) Razón Social
- (D2) CUIT

### TRANSPORTISTA — DATOS DEL TRANSPORTISTA
- (E1) Razón Social
- (E2) CUIT
- (E3) Domicilio fiscal
- (E4) Apellido y nombre del chofer
- (E5) Número Doc.
- (E6) Dominio del Vehículo

### DETALLE DE LA MERCADERÍA TRANSPORTADA
- (F1) Código AFIP
- (F2) Descripción
- (F3) Unidades / Kilogramos
- (F4) Firma
- (F5) Son nn hojas
- `"N° de Tropa"`

---

## Datos que contiene el remito según el caso correspondiente

### SECTOR A: CARÁTULA
1. Nro `<Punto de emisión asociado>` - `<Número de comprobante>`
2. `"HOJA nn de mmm"` — hoja número nn de la mmm cantidad de hojas que demande la emisión.
3. Fecha y hora de emisión.
4. Fecha y hora de emisión + Plazo S/ Tabla.

### SECTOR B: DATOS DEL TITULAR
1. Lo coloca el sistema.
2. Número de CUIT.
3. Lo coloca el sistema.

### SECTOR C: DATOS DEL DEPOSITANTE
1. Lo coloca el sistema.
2. Número de CUIT.
3. Lo coloca el sistema.

### SECTOR D: DATOS DEL DESTINATARIO
1. Lo coloca el sistema.
2. Número de CUIT.
3. Lo coloca el sistema.

### SECTOR E: DATOS DEL TRANSPORTISTA
1. Lo coloca el sistema.
2. Número de CUIT.
3. Lo coloca el sistema.
4. Lo coloca el sistema. *(Optativo)*
5. Número de Documento. *(Optativo)*
6. Dominio del vehículo que transporta la mercadería.

### SECTOR F: DETALLE DE LA MERCADERÍA TRANSPORTADA
1. Número de código que se asignará a la descripción de cada fila de las tablas de mercaderías.
2. Seleccionado de Tabla.
3. Requiere las unidades de medida **"UNIDADES"** y **"KILOS"**.
4. `"Firma"`.
5. `"SON nnn HOJAS"`, con nn cantidad de hojas que demande la emisión.
