# Trabajo Práctico — Práctica Profesionalizante I

> Proyecto: **ROCCA** — Registro de Operadores y Control de la Cadena Cárnica de Santiago del Estero
>
> Fuentes: `especificaciones/especificaciones.md`, `especificaciones/requerimiento-oficial.md`, `especificaciones/borradores/`

---

## Parte 1: Identificación de la Institución y Necesidades

### 1.1 Identificación de la institución

| Dato | Detalle |
| --- | --- |
| **Organismo** | Ministerio de Producción de la Provincia de Santiago del Estero |
| **Dirección a cargo** | Dirección General de Agricultura y Ganadería |
| **Programa** | ProCarne Fiscalización (Control de la Cadena Cárnica) |
| **Sistema a desarrollar** | ROCCA — Registro de Operadores y Control de la Cadena Cárnica de Santiago del Estero |
| **Predecesor** | ROC — Registro de Operadores de la Carne (en proceso de implementación) |
| **Referente** | Ing. (Agrónoma) Julia Luna — Área de Producción / Inspección |
| **Ámbito** | Provincia de Santiago del Estero (territorio completo) |

### 1.2 Estructura organizativa relevante

El Ministerio de Producción posee múltiples áreas con incumbencias dispares. El proyecto ROCCA se enmarca estrictamente en la **Dirección General de Agricultura y Ganadería**, a través del programa **ProCarne Fiscalización**.

**Actores del sistema:**

| Actor | Rol | Acceso |
| --- | --- | --- |
| **Inspector** | Personal de campo de ProCarne Fiscalización | Web responsiva en dispositivo móvil, con y sin conexión |
| **Operador** | Establecimiento de la cadena cárnica (12 categorías) | [PENDIENTE] — ¿accede a cargar/consultar sus datos? |
| **Administrador** | Gestiona datos maestros, habilitaciones, usuarios y bandeja de fiscalización | Web de escritorio |
| **Público general** | Consumidor que consulta operadores verificados | Web pública, sin autenticación |
| **Organismos nacionales** | ARCA, Senasa (SIGSA/AGROTRAZA) | [PENDIENTE] — integración o intercambio documental |

**Operadores alcanzados (inscripción obligatoria):**
Frigoríficos, Mataderos, Matarifes abastecedores, Abastecedores, Distribuidores, Transportistas de productos cárnicos, Carnicerías, Supermercados, Cámaras frigoríficas, Elaboradores de chacinados, Despostaderos, y todo otro operador que intervenga en la cadena comercial de carnes.

### 1.3 Misión de la institución

La misión del Ministerio de Producción, a través de la Dirección General de Agricultura y Ganadería, es **fortalecer las capacidades de fiscalización del Estado provincial** sobre la cadena cárnica, garantizando la seguridad alimentaria, la transparencia comercial y el desarrollo productivo sostenible del sector ganadero.

### 1.4 Necesidades de software

**Problemática identificada:**

1. **Sin registro integral** de operadores, la Provincia no conoce quiénes operan en la cadena ni con qué vigencia.
2. **Sin trazabilidad comercial**, no se puede conocer el origen y destino de la carne, detectar desvíos comerciales ni inconsistencias documentales.
3. **Fiscalización reactiva y de baja cobertura:** los establecimientos esconden lo que no tienen en regla, y el público no tiene información confiable para elegir dónde comprar.
4. **Sin información estratégica**, no se pueden diseñar políticas de incentivo a la faena local ni cuantificar la carne que entra y sale de la provincia.

**Necesidad central:** Un sistema único provincial que registre a todos los operadores, trace la carne comercialmente, soporte la fiscalización en campo (incluyendo operación offline) y genere información estratégica para la toma de decisiones.

**Objetivos del sistema:**

| # | Objetivo |
| --- | --- |
| OE-1 | Registrar la totalidad de los operadores de la cadena cárnica provincial |
| OE-2 | Identificar el origen y destino comercial de los productos cárnicos |
| OE-3 | Conocer los volúmenes de ingreso y circulación de carnes dentro de la provincia |
| OE-4 | Detectar desvíos comerciales e inconsistencias documentales |
| OE-5 | Facilitar la planificación de operativos de fiscalización |
| OE-6 | Elaborar indicadores económicos y productivos del sector |
| OE-7 | Facilitar el trabajo de los inspectores de carne en campo, con operación offline |
| OE-8 | Exponer al público el estado de los operadores verificados (transparencia comercial) |
| OE-9 | Incentivar la formalización y la faena en origen |

---

## Parte 2: Catálogo de Requisitos y Modelo Conceptual

### 2.1 Catálogo de Requisitos

#### 2.1.1 Requisitos Funcionales

**Módulo I — Registro Provincial de Operadores**

| ID | Requisito | Tipo |
| --- | --- | --- |
| RF-REG-01 | Registrar operadores con: datos identificatorios, habilitaciones, inscripciones nacionales y provinciales, actividad desarrollada, domicilios operativos | Conducta |
| RF-REG-02 | Mantener el estado registral de cada operador (activo / inactivo / en trámite / vencido) | Conducta |
| RF-REG-03 | Administrar el padrón de operadores de todos los tipos | Conducta |
| RF-REG-04 | Cargar y actualizar habilitaciones con fechas de emisión y vencimiento (base del semáforo) | Conducta |
| RF-REG-05 | Importar la base de datos provincial existente como carga inicial del padrón | Conducta |

**Módulo II — Trazabilidad Comercial**

| ID | Requisito | Tipo |
| --- | --- | --- |
| RF-TRA-01 | Registrar el ingreso de carnes a la provincia | Conducta |
| RF-TRA-02 | Registrar el origen de la mercadería y el establecimiento de faena | Conducta |
| RF-TRA-03 | Vincular el número de DTE y el número de remito de cada movimiento | Conducta |
| RF-TRA-04 | Registrar cantidad de kilogramos, especie y destino comercial | Conducta |
| RF-TRA-05 | Reconstruir la trazabilidad comercial completa de un producto desde la faena hasta el destino final | Conducta |

**Módulo III — Fiscalización**

| ID | Requisito | Tipo |
| --- | --- | --- |
| RF-FIS-01 | Registrar inspecciones de establecimientos, geolocalizadas | Conducta |
| RF-FIS-02 | Registrar actas, decomisos, infracciones, sanciones y reincidencias | Conducta |
| RF-FIS-03 | El inspector inicia sesión con su usuario | Conducta |
| RF-FIS-04 | Guardar el formulario de inspección en cualquier momento, incluso sin conexión | Conducta |
| RF-FIS-05 | Sincronizar las inspecciones guardadas cuando se recupere la conectividad | Conducta |
| RF-FIS-06 | Generar una observación o multa ante faltantes detectados | Conducta |
| RF-FIS-07 | Registrar en la observación: lugar, fecha, hora, foto (si es posible) y posición GPS | Conducta |
| RF-FIS-08 | Levantar un ticket ante un problema detectado en faenadores o mataderos | Conducta |
| RF-FIS-09 | Consultar el historial de inspecciones y observaciones de un establecimiento | Conducta |
| RF-FIS-10 | Gestionar la bandeja de observaciones y multas: estado, seguimiento y resolución | Conducta |
| RF-FIS-11 | Registrar reincidencias por operador | Conducta |

**Módulo IV — Información Estratégica**

| ID | Requisito | Tipo |
| --- | --- | --- |
| RF-INF-01 | Estadísticas de faena provincial | Información |
| RF-INF-02 | Estadísticas de ingreso de carnes extraprovinciales | Información |
| RF-INF-03 | Distribución territorial de operadores y movimientos | Información |
| RF-INF-04 | Consumo aparente de carne en la provincia | Información |
| RF-INF-05 | Evolución de operadores registrados | Información |
| RF-INF-06 | Indicadores económicos de la cadena cárnica | Información |
| RF-INF-07 | Mapas de calor de infracciones y de establecimientos en regla | Información |
| RF-INF-08 | Generar reportes exportables | Conducta |

**Módulo V — Portal Público de Operadores Verificados**

| ID | Requisito | Tipo |
| --- | --- | --- |
| RF-PUB-01 | Mostrar en un mapa provincial todos los operadores verificados, con su ubicación | Conducta |
| RF-PUB-02 | Consultar el estado de un operador concreto | Conducta |
| RF-PUB-03 | Semáforo de habilitación: 🟢 vigente, 🟡 próxima a vencer, 🔴 vencida | Conducta |
| RF-PUB-04 | Filtrar por estado, localidad, tipo de operador y especie | Conducta |
| RF-PUB-05 | Dar visibilidad comercial a los operadores registrados | Conducta |

**Módulo VI — Programa de Incentivos**

| ID | Requisito | Tipo |
| --- | --- | --- |
| RF-INC-01 | Gestionar el programa de incentivos a la formalización y a la faena en origen | Conducta |
| RF-INC-02 | Incentivar la registración y declaración de movimientos comerciales | Conducta |
| RF-INC-03 | Otorgar visibilidad positiva a los operadores en regla | Conducta |

**Módulo VII — Movimientos Comerciales**

| ID | Requisito | Tipo |
| --- | --- | --- |
| RF-MOV-01 | Declarar ingresos y egresos de carnes | Conducta |
| RF-MOV-02 | Vincular DTE y remitos en la declaración | Conducta |
| RF-MOV-03 | Generar constancias provinciales de los movimientos | Conducta |
| RF-MOV-04 | Confirmar recepciones (equivalente provincial a la conformidad de recepción del REC) | Conducta |
| RF-MOV-05 | Construir la trazabilidad comercial completa a partir de las declaraciones | Conducta |

**Motor de Semáforo**

| ID | Regla | Tipo |
| --- | --- | --- |
| RF-SEM-01 | 🟢 Verde: habilitación vigente, dentro del período de validez | Regla de negocio |
| RF-SEM-02 | 🟡 Amarillo: habilitación próxima a vencer | Regla de negocio |
| RF-SEM-03 | 🔴 Rojo: habilitación vencida | Regla de negocio |

**Administración (transversal)**

| ID | Requisito | Tipo |
| --- | --- | --- |
| RF-ADM-01 | Administrar usuarios (inspectores, administradores) y roles | Conducta |
| RF-ADM-02 | Gestionar la bandeja de observaciones y multas | Conducta |
| RF-ADM-03 | Generar reportes y las capas de mapas de calor | Conducta |
| RF-ADM-04 | Auditoría de accesos y de cambios sobre los expedientes | Conducta |

#### 2.1.2 Requisitos No Funcionales

| ID | Requisito | Categoría |
| --- | --- | --- |
| RNF-01 | Aplicación web responsiva; no se entrega APK | Usabilidad |
| RNF-02 | Operación offline obligatoria: el inspector trabaja en lugares remotos sin internet y no debe perder datos | Confiabilidad |
| RNF-03 | Persistencia local del formulario y de las evidencias (foto) mientras no hay red | Confiabilidad |
| RNF-04 | Geolocalización del dispositivo en el momento de la inspección; sin señal se usa la última posición conocida | Funcionalidad |
| RNF-05 | Captura de foto desde la cámara del dispositivo, tolerante a la falta de señal | Funcionalidad |
| RNF-06 | Toda evidencia queda asociada a su observación: fecha, hora, lugar, GPS y foto | Integridad |
| RNF-07 | Autenticación de usuarios del Organismo; los datos del expediente son visibles solo para personal autorizado | Seguridad |
| RNF-08 | Integridad y trazabilidad de cambios: toda modificación de un expediente debe quedar auditada | Seguridad |
| RNF-09 | Soporte de mapa provincial completo, con agrupación de marcadores (clustering) | Rendimiento |
| RNF-10 | Interfaz en español, pensada para usuarios no técnicos en campo | Usabilidad |
| RNF-11 | Escalabilidad: la provincia maneja un volumen alto de establecimientos, inspecciones y movimientos comerciales | Rendimiento |
| RNF-12 | Invariancia fiscal: el sistema no crea cargas tributarias ni restricciones al comercio interjurisdiccional | Restricción legal |

#### 2.1.3 Reglas de Negocio

| ID | Regla |
| --- | --- |
| RN-01 | El circuito de la carne es ganado → faenador/matadero → carnicería → consumidor; cada eslabón debe poder verificarse |
| RN-02 | El tránsito de animales en pie se ampara con el DUT; una vez faenado, rige la normativa fiscal y sanitaria del transporte de carnes (REC) |
| RN-03 | El frigorífico está obligado a emitir el REC, único documento válido para el traslado de carnes; el receptor debe confirmar la recepción (aceptar/rechazar) |
| RN-04 | Las reses que salen de un matadero deben tener sello de trazabilidad de SENASA [? por confirmar] |
| RN-05 | Ante faltantes de sellos se genera una observación de multa, con lugar, fecha, hora, foto y posición GPS |
| RN-06 | Un establecimiento vencido se marca en rojo y deja de ser considerado habilitado a los efectos del semáforo |
| RN-07 | La habilitación para carne vacuna y la de carne de cerdo pueden tener requisitos y vigencias distintas [?] |
| RN-08 | Los traslados directos de exportación y el reparto de supermercados desde sus centros de distribución a sucursales quedan exceptuados del REC |
| RN-09 | Todo operador de la cadena debe inscribirse obligatoriamente en el ROCCA |
| RN-10 | Los movimientos comerciales declarados (Módulo VII) generan constancias provinciales y alimentan la trazabilidad comercial (Módulo II) |

### 2.2 Modelo de Contexto

**Sistema ROCCA** interactúa con los siguientes actores externos:

![Modelo de Contexto](diagramas/contexto.png)

*Fuente: [diagramas/contexto.drawio](diagramas/contexto.drawio)*

**Interacciones principales:**

| Actor | Interacción |
| --- | --- |
| Inspector | Inicia sesión, registra inspecciones, genera observaciones/multas, consulta historial |
| Operador | [PENDIENTE] Declara movimientos comerciales, consulta su estado, responde observaciones |
| Administrador | Gestiona padrón, habilitaciones, usuarios, bandeja de fiscalización |
| Público general | Consulta mapa de operadores verificados, estado de habilitación |
| ARCA (REC) | [?] Vinculación de remitos electrónicos cárnicos |
| Senasa (DUT/DT-e) | [?] Vinculación de tránsitos de animales en pie |
| Senasa (SIGSA) | [?] Vinculación de registros sanitarios |
| Senasa (AGROTRAZA) | Convenio vigente desde 17/09/2026; acceso del Ministerio provincial ya otorgado |

### 2.3 Modelo de Requisitos (Casos de Uso)

**Actor: Inspector**

| Caso de Uso | Descripción |
| --- | --- |
| Iniciar sesión | El inspector se autentica con su usuario y contraseña |
| Registrar inspección | El inspector completa el formulario de inspección de un establecimiento, geolocalizado |
| Guardar inspección offline | El inspector guarda el formulario en el dispositivo sin conexión a internet |
| Sincronizar inspecciones | Al recuperar conectividad, el sistema envía las inspecciones pendientes |
| Generar observación/multa | El inspector registra una infracción detectada, con evidencia (foto, GPS, fecha, hora) |
| Consultar historial | El inspector consulta el historial de inspecciones y observaciones de un establecimiento |

**Actor: Operador**

| Caso de Uso | Descripción |
| --- | --- |
| Declarar movimiento comercial | El operador declara un ingreso o egreso de carnes, vinculando DTE y remito |
| Confirmar recepción | El operador receptor confirma la recepción de un movimiento comercial |
| Consultar estado | El operador consulta su estado registral y habilitaciones [PENDIENTE] |

**Actor: Administrador**

| Caso de Uso | Descripción |
| --- | --- |
| Gestionar padrón | El administrador carga y actualiza los datos de los operadores |
| Gestionar habilitaciones | El administrador carga y actualiza habilitaciones con fechas de emisión y vencimiento |
| Gestionar usuarios | El administrador crea, edita y desactiva usuarios del sistema |
| Gestionar bandeja de fiscalización | El administrador da seguimiento a observaciones y multas |
| Generar reportes | El administrador genera reportes y mapas de calor |

**Actor: Público general**

| Caso de Uso | Descripción |
| --- | --- |
| Consultar mapa de operadores | El ciudadano consulta el mapa provincial con los operadores verificados |
| Filtrar operadores | El ciudadano filtra por estado, localidad, tipo de operador y especie |
| Consultar estado de operador | El ciudadano consulta el semáforo de habilitación de un operador concreto |

---

## Parte 3: Diseño Inicial

### 3.1 Arquitectura del Software

**Estilo arquitectónico:** Web responsiva con soporte offline-first

**Componentes principales:**

![Arquitectura del Software](diagramas/arquitectura.png)

*Fuente: [diagramas/arquitectura.drawio](diagramas/arquitectura.drawio)*

**Decisiones de diseño:**

1. **Offline-first:** El inspector trabaja en zonas rurales sin señal. La aplicación debe funcionar completamente sin conexión, persistiendo datos localmente (IndexedDB/LocalStorage) y sincronizando al recuperar red.
2. **Web responsiva:** No se entrega APK ni app nativa. Se utiliza PWA (Progressive Web App) para habilitar capacidades offline.
3. **API REST:** Comunicación entre cliente y servidor mediante API REST con autenticación (JWT o similar).
4. **Base de datos relacional:** PostgreSQL o similar para almacenar el padrón de operadores, inspecciones, movimientos comerciales, etc.
5. **Almacén de evidencias:** Fotos y archivos de evidencia se almacenan en un sistema de archivos o almacenamiento en la nube, con referencia en la base de datos.
6. **Integraciones:** [PENDIENTE] Definir si se integra con ARCA/Senasa mediante API o si se limita a referencia documental (números de DTE/remito).

### 3.2 Diseño de Datos

**Diagrama Entidad-Relación (ER)**

![Diagrama Entidad-Relación](diagramas/er.png)

*Fuente: [diagramas/er.drawio](diagramas/er.drawio)*

**Descripción de entidades:**

| Entidad | Descripción | Relación principal |
| --- | --- | --- |
| **Usuario** | Persona autorizada (inspector o administrador) | 1:N con Inspección (como inspector) |
| **Operador** | Establecimiento de la cadena cárnica (12 categorías) | 1:N con Habilitación, Inscripción, Inspección, Movimiento Comercial, Sanción |
| **Habilitación** | Autorización para operar, con vigencia | N:1 con Operador |
| **Inscripción** | Registro en organismos nacionales/provinciales | N:1 con Operador |
| **Inspección** | Visita de fiscalización en campo | N:1 con Operador, N:1 con Usuario (inspector) |
| **Sello Verificado** | Verificación de sello de trazabilidad | N:1 con Inspección |
| **Observación** | Infracción detectada en inspección | N:1 con Inspección |
| **Evidencia** | Foto o archivo asociado a una observación | N:1 con Observación |
| **Movimiento Comercial** | Ingreso/egreso de carnes con DTE y remito | N:1 con Operador (origen y destino) |
| **Sanción** | Consecuencia de una observación | N:1 con Operador, N:1 con Observación |
| **Auditoría** | Registro de acciones de usuarios | N:1 con Usuario |

### 3.3 Diagramas de Subsistemas y Colaboración

**Subsistema 1: Registro de Operadores (Módulo I)**

```
┌─────────────────────────────────────────────────────────────┐
│                  Subsistema de Registro                      │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Servicio   │  │  Servicio   │  │  Servicio   │        │
│  │  de         │  │  de         │  │  de         │        │
│  │  Operadores │  │  Habilita-  │  │  Inscrip-   │        │
│  │             │  │  ciones     │  │  ciones     │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          │                                 │
│              ┌───────────┴───────────┐                     │
│              │  Repositorio de       │                     │
│              │  Operadores           │                     │
│              └───────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

**Subsistema 2: Fiscalización (Módulo III)**

```
┌─────────────────────────────────────────────────────────────┐
│                  Subsistema de Fiscalización                 │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Servicio   │  │  Servicio   │  │  Servicio   │        │
│  │  de         │  │  de         │  │  de         │        │
│  │  Inspeccio- │  │  Observa-   │  │  Sanciones  │        │
│  │  nes        │  │  ciones     │  │             │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          │                                 │
│              ┌───────────┴───────────┐                     │
│              │  Repositorio de       │                     │
│              │  Fiscalización        │                     │
│              └───────────────────────┘                     │
│                          │                                 │
│              ┌───────────┴───────────┐                     │
│              │  Servicio de          │                     │
│              │  Evidencias (fotos,   │                     │
│              │  GPS, fecha/hora)     │                     │
│              └───────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

**Subsistema 3: Trazabilidad Comercial (Módulos II y VII)**

```
┌─────────────────────────────────────────────────────────────┐
│              Subsistema de Trazabilidad Comercial            │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Servicio   │  │  Servicio   │  │  Servicio   │        │
│  │  de         │  │  de         │  │  de         │        │
│  │  Movimien-  │  │  Declara-   │  │  Confirma-  │        │
│  │  tos        │  │  ciones     │  │  ción de    │        │
│  │             │  │             │  │  Recepción  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          │                                 │
│              ┌───────────┴───────────┐                     │
│              │  Repositorio de       │                     │
│              │  Movimientos          │                     │
│              └───────────────────────┘                     │
│                          │                                 │
│              ┌───────────┴───────────┐                     │
│              │  Integración con      │                     │
│              │  ARCA (REC) y         │                     │
│              │  Senasa (DUT)         │                     │
│              │  [PENDIENTE]          │                     │
│              └───────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

**Diagrama de Colaboración: Inspección en Campo (Offline)**

```
Inspector        Web App (PWA)       Almacén Local       Servidor
   │                  │                   │                  │
   │──Inicia sesión──▶│                   │                  │
   │                  │──Verifica credenciales──────────────▶│
   │                  │◀─────────────────────────────────────│
   │◀─────────────────│                   │                  │
   │                  │                   │                  │
   │──Selecciona─────▶│                   │                  │
   │   establecimiento│                   │                  │
   │                  │──Carga padrón────▶│                  │
   │                  │◀─────────────────│                  │
   │                  │                   │                  │
   │──Completa───────▶│                   │                  │
   │   formulario     │                   │                  │
   │                  │                   │                  │
   │──[GUARDAR]──────▶│                   │                  │
   │                  │──Persiste────────▶│                  │
   │                  │◀─────────────────│                  │
   │◀─────────────────│                   │                  │
   │                  │                   │                  │
   │──[GUARDAR Y      │                   │                  │
   │   ENVIAR]───────▶│                   │                  │
   │                  │──Verifica red────▶│                  │
   │                  │◀─────────────────│                  │
   │                  │                   │                  │
   │                  │──Si hay red──────▶│                  │
   │                  │   envía al───────▶│                  │
   │                  │   servidor        │                  │
   │                  │                   │                  │
   │                  │──Al recuperar────▶│                  │
   │                  │   conectividad,   │                  │
   │                  │   sincroniza      │                  │
   │                  │   pendientes─────▶│                  │
   │                  │                   │                  │
```

### 3.4 Diseño de Interfaces Técnicas

**API REST (principales endpoints):**

```
# Autenticación
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me

# Operadores
GET    /api/operadores
POST   /api/operadores
GET    /api/operadores/:id
PUT    /api/operadores/:id
DELETE /api/operadores/:id

# Habilitaciones
GET    /api/operadores/:id/habilitaciones
POST   /api/operadores/:id/habilitaciones
PUT    /api/habilitaciones/:id

# Inspecciones
GET    /api/inspecciones
POST   /api/inspecciones
GET    /api/inspecciones/:id
PUT    /api/inspecciones/:id

# Observaciones
GET    /api/observaciones
POST   /api/observaciones
GET    /api/observaciones/:id
PUT    /api/observaciones/:id

# Movimientos Comerciales
GET    /api/movimientos
POST   /api/movimientos
GET    /api/movimientos/:id
POST   /api/movimientos/:id/confirmar-recepcion

# Reportes
GET    /api/reportes/estadisticas
GET    /api/reportes/mapas-calor
GET    /api/reportes/exportar

# Portal Público
GET    /api/publico/operadores
GET    /api/publico/operadores/:id
GET    /api/publico/semaphore/:id
```

**Formato de respuesta (JSON):**

```json
{
  "success": true,
  "data": { ... },
  "message": "Operación exitosa"
}
```

**Errores:**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "El campo CUIT es obligatorio",
    "details": [ ... ]
  }
}
```

### 3.5 Gráficos y Navegación

**Flujo de navegación principal:**

```
┌─────────────────────────────────────────────────────────────┐
│                        Login                                 │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Dashboard                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Operadores │  │  Inspeccio- │  │  Movimien-  │        │
│  │  (Mód. I)   │  │  nes (Mód.  │  │  tos        │        │
│  │             │  │   III)      │  │  (Mód. VII) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Informa-   │  │  Portal     │  │  Reportes   │        │
│  │  ción       │  │  Público    │  │  (Mód. IV)  │        │
│  │  Estratégica│  │  (Mód. V)   │  │             │        │
│  │  (Mód. IV)  │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

**Flujo de inspección (offline):**

```
┌─────────────────────────────────────────────────────────────┐
│  1. Iniciar sesión                                          │
│  2. Seleccionar establecimiento (padrón sincronizado)       │
│  3. Completar formulario de inspección                      │
│  4. [GUARDAR] → Persiste localmente                         │
│  5. [GUARDAR Y ENVIAR] → Persiste y envía si hay red        │
│  6. Al recuperar conectividad, sincroniza pendientes        │
└─────────────────────────────────────────────────────────────┘
```

**Flujo de consulta pública:**

```
┌─────────────────────────────────────────────────────────────┐
│  1. Ciudadano entra al portal                               │
│  2. Ve el mapa provincial con operadores verificados        │
│  3. Filtra o busca un operador                              │
│  4. Consulta su semáforo de habilitación                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Resumen de Pendientes

| # | Pendiente | Impacto |
| --- | --- | --- |
| 1 | Definir nivel de integración con ARCA/Senasa (API, importación, o referencia documental) | Alto — condiciona arquitectura de Módulos II y VII |
| 2 | Definir mecanismo concreto de incentivos (Módulo VI) | Medio — afecta alcance del Módulo VI |
| 3 | Definir quién declara movimientos comerciales y con qué periodicidad (Módulo VII) | Alto — afecta diseño del Módulo VII |
| 4 | Confirmar si los operadores tienen acceso al sistema | Medio — afecta diseño de interfaces |
| 5 | Definir cuántos días de anticipación para el semáforo amarillo | Bajo — afecta regla de negocio |
| 6 | Relevamiento de la base de datos provincial existente (formato, calidad, cobertura) | Medio — afecta carga inicial |
