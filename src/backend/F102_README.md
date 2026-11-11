# Generación del Formulario F 102 (Cartón Provincial)

## Resumen

El Formulario F 102 es el cartón de inscripción provincial para operadores
de la cadena cárnica. Se genera como PDF usando **pdfme** (motor de
plantillas PDF) y se muestra en un modal dentro del padrón de operadores.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│  FRONTEND (React + Vite)                                            │
│                                                                     │
│  CartonF102Modal.tsx                                                │
│    └─ useObtenerCartonF102Query(operador.id)                        │
│         └─ GET /api/f102?id={id}   (RTK Query, baseUrl=/api)        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
     ┌────────▼────────┐              ┌────────▼────────┐
     │  DESARROLLO     │              │  PRODUCCIÓN     │
     │  (local)        │              │  (Vercel)       │
     │                 │              │                 │
     │  Vite proxy     │              │  vercel.json    │
     │  /api → :8001   │              │  routes:        │
     │                 │              │  /api/f102 →    │
     │  FastAPI        │              │    api/f102.mjs │
     │  /api/f102      │              │  /api/* →       │
     │    └─ subprocess│              │    app/main.py  │
     │       node      │              │                 │
     │       generar_  │              │  Serverless     │
     │       f102.mjs  │              │  Function       │
     │                 │              │  (Node.js)      │
     │                 │              │  api/f102.mjs   │
     └─────────────────┘              └─────────────────┘
              │                                 │
              └────────────────┬────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  @pdfme/generator   │
                    │  (Node.js)          │
                    │                     │
                    │  Template:          │
                    │  template-certif... │
                    │  -operador.json     │
                    │                     │
                    │  Logos:             │
                    │  app/assets/logos/  │
                    └─────────────────────┘
```

## Flujo de datos

1. El usuario hace clic en **"Ver F102"** en el padrón de operadores.
2. El frontend llama a `GET /api/f102?id={operadorId}`.
3. El backend (local o Vercel) genera el PDF con `@pdfme/generator`:
   - Carga el template `template-certificado-operador.json`.
   - Inyecta los datos del operador (mock + datos reales de la BD).
   - Inyecta los logos institucionales (base64).
   - Renderiza el PDF (~1 MB).
4. Devuelve JSON en formato `FileTangoInfo`:
   ```json
   {
     "fileContents": "<base64 del PDF>",
     "contentType": "application/pdf",
     "fileDownloadName": "F102-100001.pdf",
     "lastModified": null,
     "entityTag": null,
     "enableRangeProcessing": false
   }
   ```
5. El frontend convierte el base64 a un `Blob` y lo muestra en un `<iframe>`.

## Archivos del flujo

### Frontend

| Archivo | Rol |
|---------|-----|
| `src/frontend/src/store/api.ts` | Endpoint RTK Query `obtenerCartonF102` → `GET /f102?id={id}` |
| `src/frontend/src/routes/modulo-i/padron/CartonF102Modal.tsx` | Modal que muestra el PDF en un iframe + botón de descarga |
| `src/frontend/src/routes/modulo-i/padron/PadronSucursales.tsx` | Botón "Ver F102" que abre el modal |

### Backend — Desarrollo local

| Archivo | Rol |
|---------|-----|
| `src/backend/app/app.py` | Endpoint `GET /api/f102?id={id}` → invoca `node generar_f102.mjs` como subprocess |
| `src/backend/generar_f102.mjs` | Script Node.js que lee el template + logos del disco y genera el PDF |
| `src/backend/app/core/pdfme/template-certificado-operador.json` | Template pdfme (~1.4 MB, incluye logos embebidos) |
| `src/backend/app/assets/logos/*.png` | Logos institucionales (4 PNG) |

### Backend — Producción (Vercel)

| Archivo | Rol |
|---------|-----|
| `src/backend/api/f102.mjs` | Serverless Function Node.js (autocontenida, no depende del filesystem) |
| `src/backend/api/f102_data.mjs` | Template + logos embebidos como base64 (~2.7 MB) |
| `src/backend/vercel.json` | Config de builds y routes: `/api/f102` → función Node, resto → FastAPI |
| `src/backend/package.json` | `"type": "module"` + dependencias `@pdfme/*` |

### Terraform / Despliegue

| Archivo | Rol |
|---------|-----|
| `terraform/main.tf` | `vercel_project` con `root_directory = "src/backend"` (sin `framework`) |

## Datos del PDF (mock)

Por ahora, los datos del F 102 son **mockeados** (estáticos). Solo el
`numero_operador` se deriva del ID real del operador:

| Campo | Valor |
|-------|-------|
| `numero_operador` | `100000 + id` (ej: `100004`) |
| `apellido_y_nombre` | `OLIVEIRA DANIEL ALBERTO` |
| `nombre_establecimiento` | `LA NORITA` |
| `razon_social` | `LA NORITA S.R.L.` |
| `cuit` | `23-30917912-9` |
| `domicilio` | `JOSE BENJAMIN ABALOS N. 4582, B. ALMIRANTE BROWN, S.D.E.` |
| `tipo_carne` | `CARNICERIAS` |
| `fecha_inscripcion` | `2025-03-10` |
| `fecha_vencimiento` | `2026-03-10` |
| `actividades` | `922210 Carniceria Minorista`, `463110 Comercializacion de carnes` |
| `inscripciones` | `PRINCIPAL 10/03/2025` |

> **TODO:** Reemplazar los datos mock por los datos reales del operador
> (BD) cuando el modelo de datos lo permita.

## Desarrollo local

### Requisitos

- Python 3.11+ con venv en `src/backend/.venv`
- Node.js 18+ (para `@pdfme/generator`)
- PostgreSQL en `localhost:5432`
- pnpm (frontend)

### Arranque

```powershell
# Desde la raíz del repo:
.\run.ps1            # build frontend + backend :8001 + Vite :5173
.\run.ps1 -NoBuild   # salta el build del frontend
```

- **Backend:** `http://localhost:8001` (FastAPI + Uvicorn)
- **Frontend:** `http://localhost:5173` (Vite dev, proxy `/api` → `:8001`)

### Probar el endpoint

```bash
curl "http://localhost:8001/api/f102?id=1" | python -m json.tool | head -5
```

### Regenerar `f102_data.mjs` (solo si cambian logos o template)

```bash
cd src/backend
.venv/Scripts/python.exe -c "
import json, base64
from pathlib import Path

template = Path('app/core/pdfme/template-certificado-operador.json').read_text()

logo_files = {
    'logo_registro_ope_carne': 'logo_registro_ope_carne.png',
    'logo_m_produccion': 'logo_m_produccion.png',
    'logo_procarne': 'logo_procarne.png',
    'logo_agricultura_ganaderia': 'logo_agricultura_ganaderia.png',
}
logos = {}
for campo, archivo in logo_files.items():
    data = Path(f'app/assets/logos/{archivo}').read_bytes()
    logos[campo] = 'data:image/png;base64,' + base64.b64encode(data).decode('ascii')

lines = [
    '// AUTO-GENERADO: No editar manualmente.',
    '// Contiene el template pdfme y los logos embebidos como base64.',
    '',
    f'export const TEMPLATE_JSON = {json.dumps(template)};',
    '',
    'export const LOGOS = {',
]
for campo, data_uri in logos.items():
    lines.append(f'  {campo}: {json.dumps(data_uri)},')
lines.append('};')
lines.append('')
Path('api/f102_data.mjs').write_text('\n'.join(lines), encoding='utf-8')
print('OK - f102_data.mjs regenerado')
"
```

## Despliegue a Vercel

```bash
cd terraform
terraform apply
```

### Cómo funciona en Vercel

- `vercel.json` define dos builds:
  - `api/*.mjs` → `@vercel/node` (Serverless Function Node.js)
  - `app/main.py` → `@vercel/python` (FastAPI)
- Rutas:
  - `/api/f102` → `api/f102.mjs` (genera PDF con pdfme)
  - `/api/*` → `app/main.py` (FastAPI, resto de la API)
  - `/*` → `app/main.py` (frontend estático)

### Variables de entorno en Vercel

| Variable | Descripción |
|----------|-------------|
| `ROCCA_DATABASE_URL` | URL de PostgreSQL (Neon/RDS) |
| `INSFORGE_URL` | URL del IdP (InsForge) |
| `INSFORGE_API_KEY` | API key de InsForge |
| `ROCCA_CORS_ORIGINS` | Orígenes permitidos (URL del frontend) |

## Notas

- El endpoint `/api/f102` está en `PUBLIC_PATHS` del middleware de auth
  (no requiere sesión). Esto es temporal mientras el F102 es mockeado.
  Cuando se integre con datos reales, se debe proteger.
- El PDF se genera en cada request (~2-3 s). Para producción con muchos
  usuarios, considerar cachear por operador_id + fecha.
- El template pdfme incluye los logos embebidos como data-URI (base64).
  Si se cambia un logo, hay que regenerar el template Y `f102_data.mjs`.
