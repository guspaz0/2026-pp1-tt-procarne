# ROCCA — Ideas Extraídas de la Entrevista con ProCarne Fiscalización

> **Origen:** Entrevista grabada (2 dispositivos, ~35 min) a la coordinadora del área de ProCarne Fiscalización, Ministerio de Producción de Santiago del Estero.
> **Contexto:** Propuesta de transformación del ROC → ROCCA. Ver `requerimiento-oficial.md`.

---

## 1. Contexto Operativo Actual

### Qué hace el área hoy
- Fiscaliza a todos los operadores de la cadena cárnica: transportistas, carnicerías, mataderos, frigoríficos, abastecedores, distribuidores, cámaras frigoríficas, elaboradores de chacinados, despostaderos.
- Doble función: **inscripción/registro** + **fiscalización** (operativos en ruta, inspecciones en establecimientos, control de condiciones higiénico-sanitarias).
- Detalle: solo intervienen sobre **animal muerto** (carnes). Lo que es animal vivo (tránsito de hacienda en pie) no es competencia directa del área, aunque lo monitorean para trazabilidad.

### Flujo de inscripción actual (manual, "al antiguo")
1. El operador trae los papeles **físicos** a la oficina (San Miguel de Tucumán Capital / La Banda).
2. Se controlan manualmente: DNI, inscripción AFIP, inscripción Rentas, papeles impositivos, últimos pagos, libreta sanitaria.
3. Se anota el punto de timbrado (tasa retributiva de servicios) — el operador debe timbrar en Rentas y traer el comprobante.
4. Se anota en una "planichita" (Excel manual) para agendar la **inspección ocular** del establecimiento.
5. Se organizan salidas **por zonas** para optimizar combustible y tiempo (norte, sur, interior).
6. Una vez hecha la inspección y constato que no hay alteraciones, se otorga la **habilitación** (troquelito rojo plastificado) con **vigencia de 1 año**.

### Problemas del flujo actual
- La gente del interior no puede viajar a la capital para dejar papeles, timbrar, etc.
- Dependencia de municipios (a veces no quieren intermediar por cuestiones políticas).
- No había registro digital hasta hace ~3 años; todo era carpetas físicas en archiveros.
- La coordinadora actual (3 años en el cargo) empezó a digitalizar a mano en Excel.
- Con la rotación de personal (licencias), las inspecciones se atrasan y los operadores trabajan con habilitación vencida.

### Trabajo ya realizado por la coordinadora (soluciones precarias)
- **Página gratuita con dominio** que muestra información del registro y requisitos por tipo de operador (carnicería, frigorífico, matadero, etc.).
- **Formulario de Google** para carga de archivos (DNI, constancia AFIP, constancia Rentas, libreta sanitaria, etc.) — el formulario guía al usuario paso a paso para que no olvide nada.
- El Excel del formulario llega al correo institucional → base de datos digital incipiente.
- Comunicación con el operador por email para observaciones (falta documento, habilitación municipal vencida, etc.).
- **Mapa de calor en Google Maps** (vía Looker Studio / Google Sheets): los inspectores cargan un formulario al hacer la inspección y se genera un punto en el mapa con color:
  - 🟢 Verde = habilitada
  - 🟡 Amarillo = con observaciones
  - 🔴 Rojo = clausurada
  - El director puede ver en tiempo real desde la oficina.
- **Limitaciones:** el mapa se desconfigura, no persiste bien, es muy precario, y el formulario Google no permite una app nativa.

---

## 2. Lo que se Pide (Necesidades)

### A. Plataforma digital de registro (reemplazar Excel + carpetas)
- Registro digital de todos los operadores (datos identificatorios, habilitaciones, inscripciones nacionales/provinciales, actividad, domicilios, estado registral).
- Carga de documentación digitalizada (archivos) con flujo guiado por tipo de operador.
- Estado del trámite visible: "documentación presentada" → "en revisión" → "pendiente timbrado" → "pendiente inspección" → "habilitado" / "observado" / "clausurado".
- Notificación al operador (email) de estado del trámite, observaciones, y vencimientos.
- **Alerta de vencimiento de habilitación** (1 año): que el operador vea cuánto falta para que venza y sea notificado con anticipación (2-3 meses).

### B. Trazabilidad comercial de carnes (el corazón del proyecto)
- Tener registro de **movimientos de carne** (no solo del animal en pie que ya está en ARCA/CENASA/SIGSA).
- Vincular: frigorífico (origen) → remito electrónico cárnico (REC) → destino (carnicería, distribuidora, supermercado).
- **Escaneo de QR en ruta**: cuando el fiscalizador detiene un camión, escanea el QR del REC con el celular y ve la información real del documento (origen, destino, kilos, categoría, vehículo) para verificar autenticidad.
- **Confirmación de recepción**: el operador que recibe la carne debe confirmar en el sistema que la mercadería llegó (balance de masa: lo que sale del frigorífico = lo que se recepciona).
- **Detectar inconsistencias**: si un frigorífico emite 1000 kg pero solo se recepcionan 400 kg, el sistema lo flaggea → herramienta para fiscalización (¿dónde está el resto?).
- Acceso a la información de ARCA/CENASA/AGROTRAZA mediante el convenio firmado (ExpoBRA, septiembre 2026) para cruzar datos.

### C. Módulo de fiscalización (inspecciones)
- Reemplazar el formulario de Google + mapa precario por una **app o página** donde el inspector:
  - Carga datos de la inspección en el celular (dirección, establecimiento, fecha, observaciones).
  - Selecciona resultado: habilitada / observada / clausurada.
  - Genera acta digital.
  - Se refleja en un **mapa de calor** en tiempo real (verde/amarillo/rojo) visible para la coordinación.
- Historial por establecimiento: todas las inspecciones, actas, decomisos, infracciones, sanciones, reincidencias.

### D. Portal público de operadores verificados
- Sección en la página del Ministerio (o subdominio) donde se listan los operadores **habilitados y en regla**.
- **Beneficio para el operador:** visibilidad comercial, "la provincia dice que soy legal" → promoción.
- El carnicero pequeño del barrio aparece en la misma plataforma que las grandes cadenas (Príncipe, El Duende) → le suma sin costo.
- **Para el consumidor:** saber que está comprando en un lugar seguro/habilitado.
- Lo privado (datos internos, infracciones, trazabilidad) NO es público — solo el hecho de estar habilitado.

### E. Historial por operador (dashboard del usuario)
- Cada operador tiene un **usuario** (como en Rentas, AFIP) con acceso a:
  - Su estado registral y vencimientos.
  - Sus infracciones y sanciones.
  - Sus movimientos de recepción de carne.
  - Sus actas de inspección.
  - Su historial completo.
- El registro/fiscalización ve el historial de **todos** los operadores.

### F. Incentivos a la formalización (Módulo VI)
- Planteado como estrategia: los operadores inscritos deberían tener prioridad en:
  - Líneas de crédito / financiamiento de nación.
  - Subsidios para la cadena cárnica.
  - Visibilidad en la página oficial de la provincia.
- "Si no me inscribo, ¿qué beneficio tengo?" → la respuesta debe ser concreta: visibilidad, acceso a créditos, prioridad en operativos de apoyo.

---

## 3. Restricciones y Consideraciones Técnicas Mencionadas

| Tema | Detalle |
|------|---------|
| **Presupuesto** | No hay líneas de financiamiento de nación actualmente. La solución debe ser realista. |
| **Página del Ministerio** | Es WordPress, obsoleta, "horrible", sin interacción. La coordinadora intentó hacer algo ahí y no pudo. Se sugiere un subdominio o página separada vinculada desde ProCarne. |
| **Equipo** | 3 personas (2 inspectores mayores + 1 coordinadora). No son técnicos. La solución debe ser **muy simple de usar**, idealmente desde el celular. |
| **Convenio AGROTRAZA** | Firmado en ExpoBRA (sep 2026). Da acceso a datos de ARCA/CENASA para la provincia. Es la base para la trazabilidad. |
| **Plazo** | Se estima ~1 año para implementación completa. Mientras tanto, seguir armando base de datos manual. |
| **Formato** | "Una página, una aplicación, lo que sea que sume." Lo más probable que sea web (están en internet, se comunican más rápido). |
| **Integración** | Idealmente extraer datos de ARCA/CENASA/AGROTRAZA (API o export) para no duplicar carga manual. |

---

## 4. Resumen de Módulos ROCCA (mapeado a lo pedido en la entrevista)

| Módulo (requerimiento oficial) | Lo que se pidió en la entrevista |
|---|---|
| **I. Registro Provincial de Operadores** | Plataforma digital de inscripción, carga de documentos, estado del trámite, alerta de vencimiento, usuario por operador. |
| **II. Trazabilidad Comercial** | Escaneo QR en ruta, confirmación de recepción, balance de masa (emisión vs. recepción), detección de inconsistencias, acceso a datos ARCA/CENASA. |
| **III. Fiscalización** | App/página para el inspector: carga de inspección en campo, resultado (habilitada/observada/clausurada), mapa de calor en tiempo real, historial de actas/infracciones/sanciones. |
| **IV. Información Estratégica** | Estadísticas de faena provincial, ingreso de carnes extraprovinciales, distribución territorial. (Mencionado indirectamente: "conocer el movimiento cárnico que hay en la provincia"). |
| **V. Portal Público** | Lista de operadores habilitados visible para el público. "Saber que está comprando en un lugar seguro." |
| **VI. Incentivos** | Prioridad en líneas de crédito/subsidios para operadores inscritos. Visibilidad en la página oficial. |
| **VII. Sistema de Movimientos Comerciales** | Declarar ingresos/egresos, vincular DTE y remitos, confirmar recepciones, constancias provinciales. |

---

## 5. Frases Clave de la Entrevistada

- *"La información que se desconoce no se puede gestionar."*
- *"Lo más importante para nosotros es la trazabilidad de la carne."*
- *"Si yo no tengo un registro de manera digital, no tengo base de datos, todo esto no lo puedo implementar."*
- *"Si nosotros no tenemos acceso a esa información del frigorífico, todo esto es el libre motor, ya no va a servir de nada."*
- *"Lo que necesito es información básicamente, poder plasmarla en una página, una aplicación."*
- *"¿Qué beneficio tengo yo inscribiéndome?"* → Problema de adopción a resolver con el portal público e incentivos.
- *"Yo les he tirado 500 mil cosas porque la verdad es que necesitamos mucho."*
- *"Ustedes tienen mucho conocimiento de la parte informática y digital, nosotros no tenemos mucha idea."*
