# Plan: Módulo I — Registro de Operadores

## Estado actual (2026-07-23)

| Área | Especificación | Estado | Notas |
|------|---------------|--------|-------|
| **Modelo Persona** | Persona física/jurídica con documento, nombre, domicilio | ✅ | ORM + DAO + Servicio + API |
| **Modelo Operador** | Operador con CUIT, tipo, categoría, persona_id, domicilio | ✅ | ORM + DAO + Servicio + API |
| **Categorías** | 8 categorías | ✅ | Incluye `CARNICERIA_CON_CAMARA` |
| **Requisitos generales** | AFIP Último Pago, Régimen Provisional | ✅ | 2 generales |
| **Requisitos específicos** | Matriz por categoría | ✅ | SALA:5, CAMARAS:7, FABRICA:12, CARNICERIAS:3, CARNICERIA_CON_CAMARA:8 |
| **Adjuntos (Persona)** | Tabla + API + Storage | ✅ | ORM + DAO + API (base64 JSON) |
| **Adjuntos (Operador)** | Tabla + API + Storage | ✅ | ORM + DAO + API (base64 JSON) |
| **Storage InsForge** | Cliente upload/download/delete | ✅ | `InsforgeStorage` (http.client) |
| **Autenticación** | Login/Signup/Refresh/Logout/Me | ✅ | InsForge BFF + cookies HttpOnly |
| **Certificados PDF** | Generación con pdfme | ✅ | `core/pdfme/` + `GET /certificado.pdf` (bytes) |
| **Jerarquía** | Agrupación por CUIT | ✅ | Client-side `Object.groupBy` |
| **Frontend: upload adjuntos** | UI de carga de archivos por requisito | ❌ | Falta todo (F1-F3) |
| **Frontend: checklist requisitos** | Mostrar requisitos pendientes/cumplidos | ⚠️ | Checkboxes sin backend |
| **Certificado vigente** | Método + endpoint + PDF base64 | ❌ | Falta B7 |
| **RBAC (roles)** | Guard de rol en POST/suspender/reactivar | ❌ | Falta B7.4 |
| **Estado PENDIENTE** | Operador nuevo → PENDIENTE → supervisor activa → ACTIVO → puede certificar | ❌ | Falta B7.5 |
| **Frontend: certificados** | Modal F102 + API + rol | ❌ | Falta F6 |

---

## Tareas pendientes de Backend

### B7 — Certificados F102 como entidad (NO IMPLEMENTADO)

> **Contexto:** Cada formulario F102 es una entidad `Certificado`. Un operador puede tener varios con distintos estados. El único válido = max(fecha_vencimiento) + max(fecha_emision). Solo ese se exporta a PDF.

#### B7.1 Método `obtener_certificado_vigente(operador_id)`
- **Archivo:** `app/modulos/registro_operadores/servicio.py`
- Consultar todos los certificados del operador
- Filtrar: `estado != RELEVADO`
- Elegir: max `fecha_vencimiento` (NULL = ∞), desempate max `fecha_emision`
- Devolver `CertificadoOut` o `None`

#### B7.2 Endpoint `GET /registro-operadores/{operador_id}/certificado-vigente`
- **Archivo:** `app/modulos/registro_operadores/controlador.py`
- `response_model=CertificadoOut | None`
- 404 si no existe

#### B7.3 PDF base64 (no bytes)
- **Archivo:** `app/modulos/registro_operadores/controlador.py`
- Modificar `GET /{operador_id}/certificado.pdf`:
  - Usar `obtener_certificado_vigente` como fuente
  - Devolver JSON: `{ "pdf_base64": "...", "nombre_archivo": "certificado-f102-{numero}.pdf", "content_type": "application/pdf" }`
  - 404 si no hay certificado válido
- `construir_certificado_data` acepta el certificado como parámetro

#### B7.4 Guard de rol + estado registral (RBAC)
- **Archivo:** `app/modulos/registro_operadores/controlador.py`
- En `POST /{operador_id}/certificados`, `POST .../suspender`, `POST .../reactivar`:
  - Leer `request.state.user.user_metadata.rol` (InsForge)
  - Si rol no es `supervisor` ni `admin` → 403
  - **El operador debe estar `ACTIVO`:** si `operador.estado_registral != ACTIVO` → 400 `"El operador debe estar ACTIVO para generar un certificado (estado actual: {estado})"`
- Helper: `def require_supervisor(request) -> None`

#### B7.5 Nuevo estado registral `PENDIENTE`
- **Ciclo de vida del operador:** `PENDIENTE` → (supervisor activa) → `ACTIVO` → (suspende) → `SUSPENDIDO` → (reactiva) → `ACTIVO` / (baja) → `BAJADO`
- Al inscribirse, el operador queda `PENDIENTE` porque el supervisor debe revisar la documentación antes de activarlo.
- Solo un operador `ACTIVO` puede generar certificados.

**B7.5a** `enums.py`: agregar `PENDIENTE = "PENDIENTE"` a `EstadoRegistral`

**B7.5b** `dao.py`: cambiar default de `estado_registral` de `ACTIVO` a `PENDIENTE`

**B7.5c** `servicio.py`: en `crear_operador`, el operador nuevo queda `PENDIENTE`

**B7.5d** `controlador.py`: nuevo endpoint `POST /{operador_id}/activar` (solo supervisor)
- Cambia `PENDIENTE → ACTIVO`
- Si ya está `ACTIVO` → 400
- Si está `BAJADO` → 400

**B7.5e** Verificar que existan `POST /{operador_id}/suspender` y `POST /{operador_id}/reactivar` para el ciclo completo (si no existen, agregarlos)

#### B7.6 Tests
- **Archivo:** `tests/modulos/registro_operadores/test_certificados.py` (nuevo)
- `test_certificado_vigente_elige_max_vencimiento`
- `test_certificado_vigente_ignora_relevado`
- `test_certificado_vigente_sin_vencimiento_infinito`
- `test_certificado_vigente_no_existe`
- `test_certificado_pdf_base64`
- `test_crear_certificado_requiere_rol` (403)
- `test_suspender_certificado_requiere_rol` (403)
- `test_operador_nuevo_estado_pendiente`
- `test_no_puede_certificar_operador_pendiente` (400)
- `test_no_puede_certificar_operador_suspendido` (400)
- `test_activar_operador_pendiente` (supervisor → ACTIVO)
- `test_activar_operador_ya_activo` (400)
- `test_certificar_operador_activo` (201)

---

## Tareas pendientes de Frontend

### F1 — Tipos y API de adjuntos (NO IMPLEMENTADO)

#### F1.1 Tipos
- **Archivo:** `src/frontend/src/types.ts`
- Agregar:
  ```ts
  interface Adjunto {
    id: number;
    requisito: string;
    storage_key: string;
    content_type: string;
    size: number;
    nombre_original: string;
    creado_en: string;
  }
  ```
- Agregar `CARNICERIA_CON_CAMARA` a las categorías

#### F1.2 API RTK Query
- **Archivo:** `src/frontend/src/store/adjuntosApi.ts` (nuevo)
- Usar `baseQueryWithAuth` (de `authGuard.ts`)
- Endpoints:
  - `subirAdjuntoPersona`: `POST /personas/{id}/adjuntos` (JSON: `{requisito, data_base64, content_type, nombre_original}`)
  - `listarAdjuntosPersona`: `GET /personas/{id}/adjuntos`
  - `obtenerUrlAdjuntoPersona`: `GET /personas/{id}/adjuntos/{adjId}/url`
  - `eliminarAdjuntoPersona`: `DELETE /personas/{id}/adjuntos/{adjId}`
  - `subirAdjuntoOperador`: `POST /registro-operadores/{id}/adjuntos`
  - `listarAdjuntosOperador`: `GET /registro-operadores/{id}/adjuntos`
  - `obtenerUrlAdjuntoOperador`: `GET /registro-operadores/{id}/adjuntos/{adjId}/url`
  - `eliminarAdjuntoOperador`: `DELETE /registro-operadores/{id}/adjuntos/{adjId}`

#### F1.3 Registrar en store
- **Archivo:** `src/frontend/src/store/store.ts`
- Agregar `adjuntosApi.reducer` al store

---

### F2 — Componente FileUpload (NO IMPLEMENTADO)

#### F2.1
- **Archivo:** `src/frontend/src/components/shared/FileUpload.tsx` (nuevo)
- Props: `requisito: string`, `adjuntoExistente?: Adjunto`, `onUploaded: () => void`
- Drag & drop + input file oculto
- Validación client-side: jpeg/png/pdf, ≤ 10 MB
- Si `adjuntoExistente`: nombre + tamaño + fecha, botones "Reemplazar" / "Eliminar"
- Convertir `File` → base64 (`FileReader.readAsDataURL`) antes de enviar
- Spinner durante upload
- Usar `useSubirAdjuntoPersonaMutation` / `useSubirAdjuntoOperadorMutation` según contexto

---

### F3 — Secciones de adjuntos en el formulario (NO IMPLEMENTADO)

#### F3.1 SeccionAdjuntosPersona
- **Archivo:** `src/frontend/src/routes/modulo-i/inscripcion/SeccionAdjuntosPersona.tsx` (nuevo)
- Props: `personaId: number`
- Grid de 4 slots: `dni_frente`, `dni_dorso`, `cuit`, `iibb`
- Cada slot: `FileUpload` con el requisito
- Estado visual: vacío (dashed) / cargado (icono)

#### F3.2 SeccionAdjuntosOperador
- **Archivo:** `src/frontend/src/routes/modulo-i/inscripcion/SeccionAdjuntosOperador.tsx` (nuevo)
- Props: `operadorId: number`, `categoria: string`
- Checklist de requisitos:
  - Generales: `afip_ultimo_pago`, `regimen_provisional` (siempre)
  - Específicos: filtrar por categoría (hardcodear matriz o fetch de API)
- Cada requisito: nombre + `FileUpload`
- Estado: pendiente (sin adjunto) / cumplido (con adjunto)

#### F3.3 Integrar en PaginaRegistroOperadores
- **Archivo:** `src/frontend/src/routes/modulo-i/inscripcion/PaginaRegistroOperadores.tsx`
- Flow: Persona → Adjuntos Persona → Operador → Adjuntos Operador
- Al crear persona: mostrar `SeccionAdjuntosPersona`
- Al crear operador: mostrar `SeccionAdjuntosOperador`

---

### F4 — Actualizar Formulario F102 (NO IMPLEMENTADO)

#### F4.1
- **Archivo:** `src/frontend/src/routes/modulo-i/inscripcion/FormularioF102.tsx`
- Agregar `CARNICERIA_CON_CAMARA` a las categorías
- Reemplazar requisitos hardcoded por los de la matriz (o fetch)
- Agregar sección de adjuntos tras el alta

#### F4.2
- **Archivo:** `src/frontend/src/store/formF102Slice.ts`
- Agregar tracking de adjuntos subidos (si es necesario)

---

### F6 — UI de Certificados (NO IMPLEMENTADO)

#### F6.1 CertificadoF102Modal
- **Archivo:** `src/frontend/src/routes/modulo-i/padron/CertificadoF102Modal.tsx` (nuevo)
- Props: `operadorId: number`, `operador: Operador`, `onClose: () => void`
- Fetch `GET /registro-operadores/{id}/certificado-vigente`
- Si existe: mostrar datos + preview PDF (base64 → Blob → iframe)
- Botón "Descargar" (Blob → `<a download>`)
- Botón "Nuevo certificado" (solo rol superior):
  - Form: número, tipo, fecha_emisión, fecha_vencimiento, actividades
  - `POST /registro-operadores/{id}/certificados`
- Si no existe: mensaje + botón crear (rol superior)

#### F6.2 certificadosApi
- **Archivo:** `src/frontend/src/store/certificadosApi.ts` (nuevo)
- RTK Query:
  - `certificadoVigente`: `GET /registro-operadores/{operadorId}/certificado-vigente`
  - `certificadoPdf`: `GET /registro-operadores/{operadorId}/certificado.pdf`
  - `crearCertificado`: `POST /registro-operadores/{operadorId}/certificados`
  - `listarCertificados`: `GET /registro-operadores/{operadorId}/certificados`

#### F6.3 Rol en auth
- **Archivo:** `src/frontend/src/store/authSlice.ts`
- Agregar `rol: string | null` al estado (leer de `user_metadata.rol` en `/me`)
- Helper: `selectEsSupervisor(state): boolean`

#### F6.4 Integrar en PadronSucursales
- **Archivo:** `src/frontend/src/routes/modulo-i/padron/PadronSucursales.tsx`
- Botón "Ver Cartón F 102" → abre `CertificadoF102Modal`
- Si el operador está `PENDIENTE`: mostrar badge "Pendiente de aprobación" + botón "Activar" (solo supervisor)
- Si el operador está `SUSPENDIDO`: mostrar badge + botón "Reactivar" (solo supervisor)

#### F6.5 Botón "Activar operador" en el padró
- **Archivo:** `src/frontend/src/routes/modulo-i/padron/PadronSucursales.tsx`
- Fila de operador `PENDIENTE` con rol superior: botón "Activar"
- Click → `POST /registro-operadores/{id}/activar` → refetch lista
- Al activar, el operador pasa a `ACTIVO` y puede generar certificados
- Agregar `activarOperador` a `certificadosApi` (o `operadoresApi`)

---

### F5 — Tests Frontend: Adjuntos (NO IMPLEMENTADO)

#### F5.1 E2E
- **Archivo:** `src/frontend/tests/e2e/adjuntos.spec.ts` (nuevo)
- Registrar operador → subir adjunto persona → verificar UI
- Subir adjunto operador → verificar checklist
- Archivo inválido → error
- Eliminar adjunto → slot vacío

#### F5.2 Component Test
- **Archivo:** `src/frontend/tests/ct/FileUpload.test.tsx` (nuevo)
- Archivo válido → dispara onUpload
- Archivo inválido → error
- Con adjuntoExistente → nombre + botones

---

### F7 — Tests Frontend: Certificados (NO IMPLEMENTADO)

#### F7.1 E2E
- **Archivo:** `src/frontend/tests/e2e/certificados.spec.ts` (nuevo)
- Abrir modal → muestra certificado vigente
- Sin certificado → mensaje + botón crear
- Crear → refetch muestra nuevo
- Descargar PDF → no 404
- Sin rol → no ve botones de creación
- Operador `PENDIENTE` → badge + botón "Activar" (supervisor)
- Activar operador → pasa a `ACTIVO` → puede crear certificado
- Operador `PENDIENTE` sin activar → no puede generar certificado (400)

---

## Resumen de archivos pendientes

### Backend — Nuevos
| Archivo | Tarea |
|---------|-------|
| `tests/modulos/registro_operadores/test_certificados.py` | B7.5 |

### Backend — Modificar
| Archivo | Tarea |
|---------|-------|
| `app/modulos/registro_operadores/servicio.py` | B7.1 |
| `app/modulos/registro_operadores/controlador.py` | B7.2, B7.3, B7.4 |

### Frontend — Nuevos
| Archivo | Tarea |
|---------|-------|
| `src/frontend/src/store/adjuntosApi.ts` | F1.2 |
| `src/frontend/src/components/shared/FileUpload.tsx` | F2.1 |
| `src/frontend/src/routes/modulo-i/inscripcion/SeccionAdjuntosPersona.tsx` | F3.1 |
| `src/frontend/src/routes/modulo-i/inscripcion/SeccionAdjuntosOperador.tsx` | F3.2 |
| `src/frontend/src/routes/modulo-i/padron/CertificadoF102Modal.tsx` | F6.1 |
| `src/frontend/src/store/certificadosApi.ts` | F6.2 |
| `src/frontend/tests/e2e/adjuntos.spec.ts` | F5.1 |
| `src/frontend/tests/ct/FileUpload.test.tsx` | F5.2 |
| `src/frontend/tests/e2e/certificados.spec.ts` | F7.1 |

### Frontend — Modificar
| Archivo | Tarea |
|---------|-------|
| `src/frontend/src/types.ts` | F1.1 |
| `src/frontend/src/store/store.ts` | F1.3 |
| `src/frontend/src/store/authSlice.ts` | F6.3 |
| `src/frontend/src/routes/modulo-i/inscripcion/PaginaRegistroOperadores.tsx` | F3.3 |
| `src/frontend/src/routes/modulo-i/inscripcion/FormularioF102.tsx` | F4.1 |
| `src/frontend/src/store/formF102Slice.ts` | F4.2 |
| `src/frontend/src/routes/modulo-i/padron/PadronSucursales.tsx` | F6.4 |

---

## Orden de ejecución

```
Backend (siguiente):
  B7.1 → B7.2 → B7.3 → B7.4 → B7.5 (PENDIENTE) → B7.6 (tests)

Frontend (paralelizable con B7):
  F1 (tipos+API) → F2 (FileUpload) → F3 (secciones) → F4 (form F102)
  F6.2 (certificadosApi) → F6.3 (rol) → F6.1 (modal) → F6.4 (integrar) → F6.5 (activar operador)

Tests (al final):
  F5 (adjuntos) + F7 (certificados)
```

### Dependencias
- F2 depende de F1 (necesita la API)
- F3 depende de F1 + F2
- F4 depende de F3
- F6.1 depende de F6.2 + F6.3
- F6.5 depende de B7.5 (endpoint activar)
- B7.3 depende de B7.1
- B7.4 depende de B7.5 (necesita saber estado PENDIENTE vs ACTIVO)
- B7.5 es prerrequisito de B7.4 (el guard de estado requiere el nuevo enum)
