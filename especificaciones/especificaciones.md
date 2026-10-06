# Especificaciones — Sistema ROCCA (ProCarne)

> Documento único de especificaciones. Consolida el **requerimiento oficial** (`requerimiento-oficial.md`) con el **relevamiento previo** (entrevista con la persona a cargo del programa ProCarne y docente de PP1), resolviendo sus cruces de forma coherente con el requerimiento oficial.
>
> Etapa: especificación, posterior a la recepción del requerimiento oficial.
>
> Convención de marcas:
>
> - **[PENDIENTE]** — no resuelto, requiere confirmación de la referente.
> - **[?]** — duda puntual a investigar o confirmar.
> - **[OFICIAL]** — viene del requerimiento oficial (ROCCA).
> - **[PREVIO]** — viene del relevamiento previo (entrevista con la persona a cargo del programa ProCarne y docente de PP1).

---

## 1. Propósito del documento

Reunir en un único documento todo lo que se conoce sobre el sistema a desarrollar: contexto institucional, problema a resolver, objetivos, alcance, requisitos funcionales y no funcionales, reglas de negocio, flujos, modelo de datos, riesgos e investigación pendiente.

El documento toma como **base normativa el requerimiento oficial de creación del ROCCA** y lo completa con el detalle operativo relevado en campo (inspección, offline, semáforo, evidencia). Donde ambos documentos se superponen, prevalece el requerimiento oficial; donde el oficial es genérico, el relevamiento aporta el detalle.

---

## 2. Contexto institucional

| Dato | Detalle |
| --- | --- |
| Organismo | Ministerio de Producción de la Provincia de Santiago del Estero |
| Órbita del sistema | Dirección General de Agricultura y Ganadería, a través del **ProCarne Fiscalización** [OFICIAL] |
| Sistema | **ROCCA** — Registro de Operadores y Control de la Cadena Cárnica de Santiago del Estero [OFICIAL] |
| Predecesor | Registro de Operadores de la Carne (ROC), en proceso de implementación; el ROCCA lo transforma y amplía [OFICIAL] |
| Ámbito | Provincia completa [OFICIAL] |
| Referente del relevamiento | Ing. (Agrónoma) Julia Luna — Área de Producción / Inspección [PREVIO] |

### 2.1 Fundamentación [OFICIAL]

La cadena cárnica es una de las actividades de mayor relevancia económica y social de la provincia. La Provincia no contó históricamente con un registro integral y actualizado de los operadores de la cadena, lo que dificultó conocer flujos comerciales, identificar operadores activos, seguir la trazabilidad y elaborar políticas basadas en evidencia.

Además, falta información objetiva sobre el volumen de animales producidos en la provincia que se faenan fuera de ella y sobre el ingreso de carnes extraprovinciales, información necesaria para diseñar políticas de incentivo a la faena local, agregado de valor en origen, fortalecimiento de frigoríficos provinciales y promoción del empleo local.

### 2.2 Contexto normativo y sistemas existentes [OFICIAL]

El sistema no opera en el vacío: existe un ecosistema nacional de trazabilidad con el que el ROCCA debe coexistir (y posiblemente integrarse):

| Sistema / Documento | Organismo | Qué gestiona |
| --- | --- | --- |
| **DUT / DT-e** | Senasa | Tránsito de animales **en pie** |
| **REC** (Remito Electrónico Cárnico) | ARCA (ex AFIP) | Único documento válido para el traslado de carnes faenadas: kilos, categoría, tipo de producto, transportista, establecimiento de destino. El receptor debe confirmar recepción (aceptar/rechazar) escaneando el QR. Exceptuados: exportación directa y reparto de supermercados desde sus C.D. a sucursales |
| **SIGSA** | Senasa | Registros sanitarios, historial de movimientos en pie, existencias en campos (Renspa), autorizaciones sanitarias del frigorífico |
| **AGROTRAZA** | Senasa | Control de insumos fitosanitarios y gestión de envases. Desde el convenio del 17/09/2026 (ExpoBRA, La Banda) se expandió a Santiago del Estero para cruzar datos de fiscalización comercial y ambiental con la producción ganadera, con acceso directo del Ministerio de Producción provincial |
| **Servidores provinciales** | Ministerio de Producción | Alojan los datos vinculados por el convenio, permitiendo auditar en tiempo real la legalidad de los cortes que circulan en el territorio |

> **[?] Pendiente:** el requerimiento oficial describe estos sistemas como contexto, pero no explicita si el ROCCA debe **integrarse** con ellos (API, carga de datos) o si la vinculación es documental/manual. Ver §12 y §13.

---

## 3. Problemática

Combinación de lo oficial y del relevamiento:

1. **Sin registro integral** de operadores, la Provincia no conoce quiénes operan en la cadena ni con qué vigencia [OFICIAL].
2. **Sin trazabilidad comercial**, no se puede conocer el origen y destino de la carne, detectar desvíos comerciales ni inconsistencias documentales [OFICIAL].
3. **Fiscalización reactiva y de baja cobertura:** los establecimientos esconden lo que no tienen en regla, y el público no tiene información confiable para elegir dónde comprar [PREVIO].
4. **Sin información estratégica**, no se pueden diseñar políticas de incentivo a la faena local ni cuantificar la carne que entra y sale de la provincia [OFICIAL].

Resultado deseado: un sistema único provincial que registre a todos los operadores, trace la carne comercialmente, soporte la fiscalización en campo y genere información estratégica para la toma de decisiones.

---

## 4. Objetivos

### 4.1 Objetivos generales [OFICIAL]

- Consolidar un sistema único de identificación y registro de los actores de la cadena cárnica provincial.
- Fortalecer la trazabilidad comercial de carnes y subproductos cárnicos.
- Generar estadísticas confiables para la toma de decisiones.
- Mejorar la transparencia comercial.
- Optimizar las tareas de fiscalización y control.
- Promover el agregado de valor en origen y la faena en establecimientos radicados en la provincia.

### 4.2 Objetivos específicos [OFICIAL + PREVIO]

| # | Objetivo | Origen |
| --- | --- | --- |
| OE-1 | Registrar la totalidad de los operadores de la cadena cárnica provincial | OFICIAL |
| OE-2 | Identificar el origen y destino comercial de los productos cárnicos | OFICIAL |
| OE-3 | Conocer los volúmenes de ingreso y circulación de carnes dentro de la provincia | OFICIAL |
| OE-4 | Detectar desvíos comerciales e inconsistencias documentales | OFICIAL |
| OE-5 | Facilitar la planificación de operativos de fiscalización | OFICIAL |
| OE-6 | Elaborar indicadores económicos y productivos del sector | OFICIAL |
| OE-7 | Facilitar el trabajo de los inspectores de carne en campo, con operación offline | PREVIO |
| OE-8 | Exponer al público el estado de los operadores verificados (transparencia comercial) | OFICIAL (Módulo V) + PREVIO |
| OE-9 | Incentivar la formalización y la faena en origen | OFICIAL (Módulo VI) + PREVIO |

---

## 5. Actores del sistema

| Actor | Descripción | Acceso | Origen |
| --- | --- | --- | --- |
| Inspector | Personal de campo de ProCarne Fiscalización | Web responsiva en dispositivo móvil, con y sin conexión | PREVIO |
| Operador | Establecimiento de la cadena (frigorífico, matadero, carnicería, transportista, etc.) | **[PENDIENTE]** — ¿accede a cargar/consultar sus datos y declaraciones? | OFICIAL (implicado por Módulos V y VII) |
| Administrador | Gestiona datos maestros de operadores, habilitaciones, usuarios y la bandeja de fiscalización | Web de escritorio | PREVIO + derivado |
| Público general | Consumidor que consulta operadores verificados | Web pública, sin autenticación | OFICIAL (Módulo V) + PREVIO |
| Organismos nacionales | ARCA, Senasa (SIGSA/AGROTRAZA) | **[PENDIENTE]** — integración o intercambio documental a definir | OFICIAL (§2.2) |

### 5.1 Operadores alcanzados (inscripción obligatoria) [OFICIAL]

- Frigoríficos
- Mataderos
- Matarifes abastecedores
- Abastecedores
- Distribuidores
- Transportistas de productos cárnicos
- Carnicerías
- Supermercados
- Cámaras frigoríficas
- Elaboradores de chacinados
- Despostaderos
- Todo otro operador que intervenga en la cadena comercial de carnes

---

## 6. Alcance

### 6.1 Dentro del alcance

**Según módulos del requerimiento oficial [OFICIAL]:**

1. **Módulo I — Registro Provincial de Operadores:** datos identificatorios, habilitaciones, inscripciones nacionales y provinciales, actividad desarrollada, domicilios operativos, estado registral.
2. **Módulo II — Trazabilidad Comercial:** ingreso de carnes a la provincia, origen de la mercadería, establecimiento de faena, número de DTE, número de remito, cantidad de kilogramos, especie, destino comercial.
3. **Módulo III — Fiscalización:** inspecciones, actas, decomisos, infracciones, sanciones, reincidencias.
4. **Módulo IV — Información Estratégica:** estadísticas de faena provincial, ingreso de carnes extraprovinciales, distribución territorial, consumo aparente, evolución de operadores registrados, indicadores económicos de la cadena.
5. **Módulo V — Portal Público de Operadores Verificados:** formalización, acceso del consumidor a establecimientos habilitados, visibilidad comercial de operadores registrados.
6. **Módulo VI — Programa Provincial de Incentivos a la Formalización y Faena en Origen:** faena provincial, fortalecimiento de frigoríficos locales, agregado de valor, incentivos a la registración y declaración de movimientos.
7. **Módulo VII — Sistema Provincial de Movimientos Comerciales de Carnes:** declaración de ingresos y egresos, vinculación de DTE y remitos, constancias provinciales, confirmación de recepciones, trazabilidad comercial completa.

**Según el relevamiento operativo [PREVIO]:**

- Aplicación **web responsiva** (no APK ni app nativa).
- Autenticación de inspectores con usuario propio.
- Registro geolocalizado de operadores en un mapa provincial.
- Semáforo de estado de habilitación por establecimiento.
- Inspección en campo con **soporte offline** (guardado local y sincronización al recuperar red).
- Registro de observaciones y multas con evidencia (foto, GPS, fecha y hora).
- Mapas de calor de infracciones y de establecimientos en regla.
- Consulta pública del estado de cada operador.
- Aprovechamiento de la base de datos provincial ya existente como fuente de registro inicial.

### 6.2 Fuera del alcance

- Emisión de habilitaciones oficiales o notificación legal de sanciones (hoy es un trámite del Ministerio) [PREVIO].
- Gestión de los sistemas internos de SENASA/ARCA [PREVIO].
- Integración con organismos o sistemas de otras provincias sin acuerdo previo [PREVIO].
- App móvil nativa / APK [PREVIO].
- Nuevas cargas tributarias o restricciones al comercio interjurisdiccional: el ROCCA es una herramienta de gestión, registro y control [OFICIAL].

### 6.3 Ajustes de alcance respecto del relevamiento previo

El requerimiento oficial **amplía** el alcance original del relevamiento:

| Aspecto | Relevamiento previo | Requerimiento oficial | Resolución |
| --- | --- | --- | --- |
| Sujetos | Carnicerías (y mataderos/frigoríficos de forma parcial) | **Todos los operadores** de la cadena (12 categorías) | Prevalece el oficial: el registro es integral |
| Trazabilidad | Sellos de SENASA, foco en la carnicería | Trazabilidad **comercial** completa (DTE, remitos, REC, kg, especie, origen/destino) | Prevalece el oficial: el ROCCA traza el movimiento comercial, no solo el sello |
| Portal público | Carnicerías habilitadas | **Operadores verificados** (todas las categorías) | Prevalece el oficial |
| Incentivos | "Incentivos para que trabajen en regla" (sin definir) | Módulo VI dedicado: formalización y faena en origen | El oficial da estructura; el mecanismo concreto sigue **[PENDIENTE]** |
| Movimientos comerciales | No contemplado | Módulo VII: declaración de ingresos/egresos, constancias provinciales | Nuevo alcance, incorporado |

---

## 7. Requisitos funcionales

### 7.1 Módulo I — Registro Provincial de Operadores [OFICIAL + PREVIO]

| ID | Requisito | Origen |
| --- | --- | --- |
| RF-REG-01 | Registrar operadores con: datos identificatorios, habilitaciones, inscripciones nacionales y provinciales, actividad desarrollada, domicilios operativos | OFICIAL |
| RF-REG-02 | Mantener el estado registral de cada operador (activo / inactivo / en trámite / vencido) | OFICIAL |
| RF-REG-03 | Administrar el padrón de operadores de todos los tipos (§5.1) | PREVIO (ampliado) |
| RF-REG-04 | Cargar y actualizar habilitaciones con fechas de emisión y vencimiento (base del semáforo) | PREVIO |
| RF-REG-05 | Importar la base de datos provincial existente como carga inicial del padrón | PREVIO |

### 7.2 Módulo II — Trazabilidad Comercial [OFICIAL]

| ID | Requisito | Origen |
| --- | --- | --- |
| RF-TRA-01 | Registrar el ingreso de carnes a la provincia | OFICIAL |
| RF-TRA-02 | Registrar el origen de la mercadería y el establecimiento de faena | OFICIAL |
| RF-TRA-03 | Vincular el número de DTE y el número de remito de cada movimiento | OFICIAL |
| RF-TRA-04 | Registrar cantidad de kilogramos, especie y destino comercial | OFICIAL |
| RF-TRA-05 | Reconstruir la trazabilidad comercial completa de un producto desde la faena hasta el destino final | derivado |

> **[?] Pendiente:** relación con el REC (ARCA) y el DUT (Senasa): ¿el ROCCA carga los datos manualmente, importa de los sistemas nacionales o se limita a referenciar los números de DTE/remito? Ver §12.

### 7.3 Módulo III — Fiscalización [OFICIAL + PREVIO]

| ID | Requisito | Origen |
| --- | --- | --- |
| RF-FIS-01 | Registrar inspecciones de establecimientos, geolocalizadas | OFICIAL + PREVIO |
| RF-FIS-02 | Registrar actas, decomisos, infracciones, sanciones y reincidencias | OFICIAL |
| RF-FIS-03 | El inspector inicia sesión con su usuario | PREVIO |
| RF-FIS-04 | Guardar el formulario de inspección en cualquier momento, incluso sin conexión | PREVIO |
| RF-FIS-05 | Sincronizar las inspecciones guardadas cuando se recupere la conectividad | PREVIO |
| RF-FIS-06 | Generar una observación o multa ante faltantes detectados (ej. sellos de trazabilidad) | PREVIO |
| RF-FIS-07 | Registrar en la observación: lugar, fecha, hora, foto (si es posible) y posición GPS | PREVIO |
| RF-FIS-08 | Levantar un ticket ante un problema detectado en faenadores o mataderos | PREVIO |
| RF-FIS-09 | Consultar el historial de inspecciones y observaciones de un establecimiento | derivado |
| RF-FIS-10 | Gestionar la bandeja de observaciones y multas: estado, seguimiento y resolución | derivado |
| RF-FIS-11 | Registrar reincidencias por operador | OFICIAL |

> **[?] Pendiente:** ¿el verificado en inspección sigue siendo la presencia/validez de sellos de trazabilidad (chips) como se relevó, o cambia con la trazabilidad comercial por DTE/remito? Ver §12.

### 7.4 Módulo IV — Información Estratégica [OFICIAL + PREVIO]

| ID | Requisito | Origen |
| --- | --- | --- |
| RF-INF-01 | Estadísticas de faena provincial | OFICIAL |
| RF-INF-02 | Estadísticas de ingreso de carnes extraprovinciales | OFICIAL |
| RF-INF-03 | Distribución territorial de operadores y movimientos | OFICIAL |
| RF-INF-04 | Consumo aparente de carne en la provincia | OFICIAL |
| RF-INF-05 | Evolución de operadores registrados | OFICIAL |
| RF-INF-06 | Indicadores económicos de la cadena cárnica | OFICIAL |
| RF-INF-07 | Mapas de calor de infracciones y de establecimientos en regla | PREVIO |
| RF-INF-08 | Generar reportes exportables | derivado |

### 7.5 Módulo V — Portal Público de Operadores Verificados [OFICIAL + PREVIO]

| ID | Requisito | Origen |
| --- | --- | --- |
| RF-PUB-01 | Mostrar en un mapa provincial todos los operadores verificados, con su ubicación | OFICIAL + PREVIO |
| RF-PUB-02 | Consultar el estado de un operador concreto | OFICIAL + PREVIO |
| RF-PUB-03 | Semáforo de habilitación: 🟢 vigente, 🟡 próxima a vencer, 🔴 vencida | PREVIO |
| RF-PUB-04 | Filtrar por estado, localidad, tipo de operador y especie (vacuno / porcino) | derivado |
| RF-PUB-05 | Dar visibilidad comercial a los operadores registrados (promover la formalización) | OFICIAL |

### 7.6 Módulo VI — Programa de Incentivos [OFICIAL + PREVIO]

| ID | Requisito | Origen |
| --- | --- | --- |
| RF-INC-01 | Gestionar el programa de incentivos a la formalización y a la faena en origen | OFICIAL |
| RF-INC-02 | Incentivar la registración y declaración de movimientos comerciales | OFICIAL |
| RF-INC-03 | Otorgar visibilidad positiva a los operadores en regla (mecanismo concreto **[PENDIENTE]**) | PREVIO |

> **[PENDIENTE]:** el mecanismo de incentivos sigue sin definir (coherente con el relevamiento previo; el oficial lo declara como objetivo pero no lo detalla).

### 7.7 Módulo VII — Movimientos Comerciales [OFICIAL]

| ID | Requisito | Origen |
| --- | --- | --- |
| RF-MOV-01 | Declarar ingresos y egresos de carnes | OFICIAL |
| RF-MOV-02 | Vincular DTE y remitos en la declaración | OFICIAL |
| RF-MOV-03 | Generar constancias provinciales de los movimientos | OFICIAL |
| RF-MOV-04 | Confirmar recepciones (equivalente provincial a la conformidad de recepción del REC) | OFICIAL |
| RF-MOV-05 | Construir la trazabilidad comercial completa a partir de las declaraciones | OFICIAL |

> **[PENDIENTE]:** ¿quién declara (operador transportista, establecimiento de origen, de destino?) y con qué periodicidad. Ver §13.

### 7.8 Motor de semáforo [PREVIO]

| ID | Regla |
| --- | --- |
| RF-SEM-01 | 🟢 **Verde:** habilitación vigente, dentro del período de validez |
| RF-SEM-02 | 🟡 **Amarillo:** habilitación próxima a vencer — **[PENDIENTE: ¿cuántos días de anticipación?]** |
| RF-SEM-03 | 🔴 **Rojo:** habilitación vencida |

### 7.9 Administración (transversal) [PREVIO + derivado]

| ID | Requisito |
| --- | --- |
| RF-ADM-01 | Administrar usuarios (inspectores, administradores) y roles |
| RF-ADM-02 | Gestionar la bandeja de observaciones y multas: estado, seguimiento y resolución |
| RF-ADM-03 | Generar reportes y las capas de mapas de calor |
| RF-ADM-04 | Auditoría de accesos y de cambios sobre los expedientes |

---

## 8. Requisitos no funcionales

| ID | Requisito | Origen |
| --- | --- | --- |
| RNF-01 | Aplicación **web responsiva**; no se entrega APK | PREVIO |
| RNF-02 | **Operación offline obligatoria:** el inspector trabaja en lugares remotos sin internet y no debe perder datos | PREVIO |
| RNF-03 | Persistencia local del formulario y de las evidencias (foto) mientras no hay red | PREVIO |
| RNF-04 | Geolocalización del dispositivo en el momento de la inspección; sin señal se usa la última posición conocida | PREVIO |
| RNF-05 | Captura de foto desde la cámara del dispositivo, tolerante a la falta de señal | PREVIO |
| RNF-06 | Toda evidencia queda asociada a su observación: fecha, hora, lugar, GPS y foto | PREVIO |
| RNF-07 | Autenticación de usuarios del Organismo; los datos del expediente son visibles solo para personal autorizado | PREVIO |
| RNF-08 | Integridad y trazabilidad de cambios: toda modificación de un expediente debe quedar auditada | PREVIO |
| RNF-09 | Soporte de mapa provincial completo, con agrupación de marcadores (clustering) — **[PENDIENTE: definir]** | PREVIO |
| RNF-10 | Interfaz en español, pensada para usuarios no técnicos en campo | PREVIO |
| RNF-11 | Escalabilidad: la provincia maneja un volumen alto de establecimientos, inspecciones y movimientos comerciales | PREVIO + derivado (Módulo VII) |
| RNF-12 | Invariancia fiscal: el sistema no crea cargas tributarias ni restricciones al comercio interjurisdiccional | OFICIAL |

---

## 9. Reglas de negocio

1. El circuito de la carne es **ganado → faenador/matadero → carnicería → consumidor**; cada eslabón debe poder verificarse [PREVIO].
2. El tránsito de animales en pie se ampara con el **DUT**; una vez faenado, rige la normativa fiscal y sanitaria del transporte de carnes (**REC**) [OFICIAL].
3. El frigorífico está obligado a emitir el **REC**, único documento válido para el traslado de carnes; el receptor debe confirmar la recepción (aceptar/rechazar) [OFICIAL].
4. Las reses que salen de un matadero deben tener **sello de trazabilidad de SENASA** **[? por confirmar]**; en la carnicería se verifica que conserven los sellos de origen [PREVIO].
5. Ante faltantes de sellos se genera una **observación de multa**, con lugar, fecha, hora, foto y posición GPS [PREVIO].
6. Un establecimiento vencido se marca en **rojo** y deja de ser considerado habilitado a los efectos del semáforo [PREVIO].
7. La habilitación para carne vacuna y la de carne de cerdo pueden tener requisitos y vigencias distintas **[?]** [PREVIO].
8. Los traslados directos de exportación y el reparto de supermercados desde sus centros de distribución a sucursales quedan **exceptuados del REC** [OFICIAL].
9. Todo operador de la cadena (§5.1) debe inscribirse obligatoriamente en el ROCCA [OFICIAL].
10. Los movimientos comerciales declarados (Módulo VII) generan constancias provinciales y alimentan la trazabilidad comercial (Módulo II) [OFICIAL, derivado].

---

## 10. Flujos principales

### 10.1 Inspección en campo (caso habitual, sin señal) [PREVIO]

```
Inspector inicia sesión
   → Selecciona establecimiento (padrón ya sincronizado)
   → Completa el formulario de inspección
   → [GUARDAR]           → se persiste en el dispositivo (funciona sin internet)
   → [GUARDAR Y ENVIAR]  → se persiste y, si hay red, se envía al servidor
   → Al recuperar conectividad se sincronizan automáticamente los pendientes
```

### 10.2 Detección de infracción [PREVIO]

```
Inspector detecta faltante de sellos / inconsistencia
   → Levanta el ticket / observación de multa
   → El sistema captura fecha, hora, GPS y foto (si es posible)
   → Se guarda (online u offline)
   → Queda en la bandeja del Administrador para su seguimiento
```

### 10.3 Consulta pública [PREVIO + OFICIAL]

```
Ciudadano entra al portal
   → Ve el mapa provincial con los operadores verificados
   → Filtra o busca un operador
   → Consulta su semáforo de habilitación
```

### 10.4 Declaración de movimiento comercial [OFICIAL, nuevo]

```
Operador (transportista / establecimiento)
   → Declara ingreso o egreso de carnes
   → Vincula DTE y número de remito (REC)
   → El sistema genera la constancia provincial
   → El receptor confirma la recepción
   → Queda incorporado a la trazabilidad comercial (Módulo II)
```

> **[PENDIENTE]:** actores, periodicidad y validaciones del flujo 10.4. Ver §13.

---

## 11. Modelo de datos inicial

Entidades tentativas, a validar en la etapa de diseño. Combina el modelo previo con las entidades implicadas por los Módulos II y VII.

| Entidad | Campos principales | Origen |
| --- | --- | --- |
| Usuario | id, nombre, usuario, hash de contraseña, rol, activo | PREVIO |
| Operador | id, tipo (12 categorías §5.1), razón social, CUIT, dirección, latitud, longitud, localidad, teléfono, especies, estado registral | PREVIO (ampliado a "Operador") |
| Habilitación | id, operador, especie, número, fecha de emisión, fecha de vencimiento, estado | PREVIO |
| Inscripción | id, operador, organismo (nacional/provincial), número, fecha, estado | derivado (Módulo I) |
| Inspección | id, inspector, operador, fecha y hora, latitud, longitud, resultado, enviada | PREVIO |
| Sello verificado | id, inspección, tipo de corte, número de sello, estado (presente / faltante / vencido / ilegible) **[? según investigación de chips]** | PREVIO |
| Observación o multa | id, inspección, tipo, descripción, estado, resolución — **[PENDIENTE: flujo de sanción]** | PREVIO |
| Evidencia | id, observación, archivo, fecha y hora, latitud, longitud | PREVIO |
| Movimiento comercial | id, operador origen, operador destino, especie, kg, fecha, DTE, remito (REC), constancia provincial, recepción confirmada | derivado (Módulos II y VII) |
| Sanción | id, operador, observación, tipo (infracción / decomiso / multa), estado, reincidencia | derivado (Módulo III) |
| Auditoría | id, usuario, acción, entidad, fecha y hora | PREVIO |

---

## 12. Integraciones y datos de origen

| Fuente | Qué aporta | Estado |
| --- | --- | --- |
| Base de datos provincial existente (carnicerías, mataderos, frigoríficos) | Carga inicial del padrón de operadores | **[PENDIENTE]:** formato, calidad y cobertura a relevar |
| DUT / DT-e (Senasa) | Tránsito de animales en pie | **[?] integración o referencia documental** |
| REC (ARCA) | Remitos electrónicos cárnicos, destinos, facturación | **[?] integración o referencia documental** |
| SIGSA (Senasa) | Registros sanitarios, existencias, autorizaciones | **[?] integración o referencia documental** |
| AGROTRAZA (Senasa) | Insumos fitosanitarios, envases, datos declarados en territorio provincial | Convenio vigente desde 17/09/2026; acceso del Ministerio provincial ya otorgado [OFICIAL] |

> **[?] Central:** el requerimiento oficial no explicita el nivel de integración con los sistemas nacionales. Tres escenarios posibles: (a) referencia documental (se cargan números de DTE/remito), (b) importación periódica de datos, (c) integración en tiempo real. Condiciona toda la arquitectura del Módulo II y VII.

---

## 13. Investigación pendiente

- [ ] **Integración con sistemas nacionales:** nivel de integración con DUT, REC (ARCA), SIGSA y AGROTRAZA (escenario a/b/c de §12).
- [ ] Rol y funcionamiento de **SENASA** en el proceso.
- [ ] Funcionamiento de **chips y sellos** de trazabilidad: ¿RFID, impresión, código? ¿Sigue siendo el objeto de verificación en inspección junto con la trazabilidad comercial?
- [ ] Descripción detallada del circuito: ganado → faenador → carnicerías.
- [ ] Requisitos de habilitación de un establecimiento para operar con **carne vacuna** y **carne de cerdo**.
- [ ] Formato, calidad y cobertura de la base de datos existente.
- [ ] Procedimiento formal de sanción por observación o multa.
- [ ] **Módulo VII:** quién declara los movimientos comerciales, con qué periodicidad, qué validaciones aplica el sistema y qué es exactamente una "constancia provincial".
- [ ] **Módulo VI:** mecanismo concreto de los incentivos a la formalización y a la faena en origen.

---

## 14. Preguntas abiertas para la Ing. Julia Luna

1. ¿Cuál es la prioridad real del primer incremento: el registro de operadores (Módulo I), la herramienta del inspector (Módulo III), el portal público (Módulo V) o los movimientos comerciales (Módulo VII)?
2. ¿El sistema debe limitarse a consultar operadores o también gestionar el trámite de habilitación?
3. ¿Cuánto tiempo se considera "próxima a vencer" para el semáforo amarillo?
4. ¿Qué incentivos están previstos para los operadores en regla? El mecanismo concreto está sin definir.
5. ¿Los mapas de calor son de infracciones, de operadores en regla, o de "mejor valorados"?
6. ¿Existe integración posible con SENASA/ARCA o el vínculo es puramente documental (números de DTE/remito, foto del sello)?
7. ¿El inspector trabaja offline en un dispositivo asignado por el Organismo o en su propio celular? Esto condiciona toda la arquitectura offline.
8. ¿Quién carga y mantiene las habilitaciones: el Administrador del Ministerio o se importan de otro sistema?
9. **¿Quiénes declaran los movimientos comerciales (Módulo VII)**: transportistas, establecimientos de origen, de destino, o todos? ¿Con qué periodicidad?
10. **¿Los operadores tienen acceso al sistema** para cargar sus datos, consultar su estado y responder a observaciones?
11. ¿Qué datos de la base de datos provincial existente están disponibles hoy y en qué formato?

---

## 15. Riesgos identificados

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | Zona rural sin señal | Alto | Diseño offline-first como requisito central (RNF-02) |
| 2 | Requisitos de trazabilidad todavía sin entender (chips, sellos, DTE, REC) | Alto | Investigación obligatoria antes de diseñar el formulario y el Módulo II |
| 3 | Base de datos de origen en formato desconocido | Medio | Relevamiento de la base actual en la próxima reunión |
| 4 | Geolocalización no disponible o imprecisa | Medio | El GPS queda como dato complementario, nunca como única evidencia |
| 5 | Fotos pesadas con mala conexión | Medio | Compresión y carga diferida de evidencias |
| 6 | Crecimiento del alcance (7 módulos, incentivos, heatmaps, integraciones) | Alto | Priorización por incrementos con la referente; el oficial define el todo, el primer incremento se acota |
| 7 | Uso indebido o difusión de los datos de inspección | Legal | Restricción a inspectores autorizados y auditoría de accesos |
| 8 | Dependencia de sistemas nacionales (ARCA, Senasa) sin acuerdo de integración firmado | Alto | Definir escenario de integración (§12) antes del diseño; fallback a referencia documental |
| 9 | Desfase entre el alcance oficial (integral) y la capacidad de entrega inicial | Medio | Mapear módulos por incremento y acordar con la referente el alcance del primero |

---

## 16. Incrementos propuestos (tentativo, a validar)

| Incremento | Módulos | Contenido |
| --- | --- | --- |
| **MVP** | I + III + V (parcial) | Registro de operadores, inspección en campo offline con observaciones/multas, portal público con mapa y semáforo |
| **2°** | II + VII | Trazabilidad comercial y declaración de movimientos comerciales (sujeto a definición de integración §12) |
| **3°** | IV + VI | Información estratégica, mapas de calor y programa de incentivos |

> Tentativo: la priorización final se define con la Ing. Julia Luna (pregunta 14.1).

---

## 17. Glosario

| Término | Definición |
| --- | --- |
| ROCCA | Registro de Operadores y Control de la Cadena Cárnica de Santiago del Estero |
| ROC | Registro de Operadores de la Carne (predecesor del ROCCA) |
| ProCarne Fiscalización | Programa del Ministerio de Producción bajo el cual funciona el ROCCA |
| DUT / DT-e | Documento Único de Tránsito (electrónico) de animales en pie (Senasa) |
| REC | Remito Electrónico Cárnico (ARCA); único documento válido para el traslado de carnes |
| ARCA | Agencia de Recaudación y Control Aduanero (ex AFIP) |
| SENASA | Servicio Nacional de Sanidad y Calidad Agroalimentaria |
| SIGSA | Sistema de información sanitaria de SENASA |
| AGROTRAZA | Sistema de SENASA de control de insumos fitosanitarios y envases; ampliado en 2026 a fiscalización ganadera/comercial en la provincia |
| DTE | Documento Tributario Electrónico |
| Faenador / Matadero | Establecimiento donde se realiza el faenado de las reses |
| Frigorífico | Establecimiento que procesa, conserva y despacha carne |
| Sello de trazabilidad | Identificación oficial del origen de la res |
| Habilitación | Autorización para operar como establecimiento habilitado |
| Observación de multa | Registro formal de una infracción detectada en una inspección |
| Constancia provincial | Documento generado por el ROCCA que acredita un movimiento comercial declarado |
| Operador | Establecimiento o persona que interviene en la cadena comercial de carnes (§5.1) |

---

## 18. Trazabilidad con las fuentes

| Sección de este documento | `requerimiento-oficial.md` | `especs_previas__unificado.md` |
| --- | --- | --- |
| §2 Contexto institucional | Fundamentación; Creación del ROCCA; Operadores alcanzados; sistemas (DUT, REC, ARCA, SIGSA, AGROTRAZA) | §2 Contexto institucional |
| §3 Problemática | Fundamentación | §3 Problemática |
| §4 Objetivos | Objetivos Generales y Específicos | §4 Objetivos |
| §5 Actores | Operadores Alcanzados; Portal Público; Movimientos Comerciales | §5 Actores |
| §6 Alcance | Componentes del Sistema (Módulos I–VII); Consideraciones Finales | §6 Alcance |
| §7 Requisitos funcionales | Módulos I–VII | §7 Requisitos funcionales |
| §8 Requisitos no funcionales | Consideraciones Finales (RNF-12) | §8 Requisitos no funcionales |
| §9 Reglas de negocio | DUT, REC, excepciones, inscripción obligatoria | §9 Reglas de negocio |
| §10 Flujos | Módulo VII (flujo 10.4) | §10 Flujos |
| §11 Modelo de datos | Módulos I, II, III, VII | §11 Modelo de datos |
| §12 Integraciones | Dónde se aloja la información; AGROTRAZA | §13 Investigación pendiente (SENASA) |
| §13 Investigación pendiente | (abre preguntas sobre integraciones) | §13 Investigación pendiente |
| §14 Preguntas abiertas | (abre preguntas 9–11) | §14 Preguntas abiertas |
| §15 Riesgos | Alcance integral (riesgo 6, 9) | §12 Riesgos |
| §16 Incrementos | Módulos I–VII | §15 Próximo paso |
