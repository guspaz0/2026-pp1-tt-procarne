# Especificaciones Previas — Sistema PROCARNE

> Documento unificado. Consolida y expande la información de `requerimientos_previos.md` y `anotaciones_previas.md`.
> Etapa: relevamiento previo a la reunión de validación con la Ing. Julia Luna.

---

## 1. Propósito del documento

Reunir en un único documento todo lo que se conoce hasta el momento sobre el sistema a desarrollar: contexto institucional, problema a resolver, alcance y requisitos funcionales y no funcionales.

Los puntos marcados como **[PENDIENTE]** o **[?]** no fueron resueltos en el relevamiento inicial y requieren confirmación de la referente antes de pasar a la etapa de diseño.

---

## 2. Contexto institucional

| Dato                   | Detalle                                                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Organismo              | Ministerio de Producción de la Provincia                                                                                  |
| Programa               | PROCAME (control de carnicerías habilitadas de la provincia)                                                              |
| Ámbito                 | Provincia completa, con múltiples áreas ministeriales                                                                     |
| Referente              | Ing. (Agrónoma) Julia Luna — Área de Producción / Inspección                                                              |
| Lugar de la entrevista | Ministerio de Producción, Torres "Barquito" (sede del Registro Civil), esquina Belgrano y Andes, torre que da sobre Andes |
| Origen del proyecto    | Facilitar el trabajo de los inspectores de carne                                                                          |

El Ministerio posee áreas con incumbencias dispares; el alcance del proyecto se limita estrictamente a PROCARNE.

---

## 3. Problemática

La inspección de carnicerías es difícil de llevar adelante porque los establecimientos **esconden lo que no tiene en regla**. En paralelo, el público general carece de información confiable para decidir **qué carnicería comprar**, ya sea por cumplimiento normativo o por calidad.

Esto genera dos efectos:

1. **Para el Organismo:** cobertura de inspección baja, fiscalización reactiva y riesgo de carne clandestina sin trazabilidad.
2. **Para el público:** decisiones de compra orientadas por precio o publicidad, y no por datos de origen.

Resultado deseado: que la carne que llega al consumidor sea trazable **desde el frigorífico/matadero hasta la carnicería**.

---

## 4. Objetivo general

> Facilitar el trabajo de los inspectores de carne del programa PROCAME y garantizar la trazabilidad del origen y destino de la carne, desde los frigoríficos y mataderos hasta las carnicerías de la provincia.

### 4.1 Objetivos específicos

| #    | Objetivo                                                                                  | Beneficiario          |
| ---- | ----------------------------------------------------------------------------------------- | --------------------- |
| OE-1 | Digitalizar y persistir el formulario de inspección en campo, aun sin conectividad        | Inspector             |
| OE-2 | Controlar la presencia y validez de los sellos de trazabilidad en mataderos y carnicerías | Inspector / SENASA    |
| OE-3 | Registrar y dar seguimiento a observaciones y multas con evidencia asociada               | Inspector / Organismo |
| OE-4 | Exponer al público el estado de habilitación de cada carnicería                           | Público general       |
| OE-5 | Generar mapas de calor que muestren la distribución de las infracciones                   | Organismo             |
| OE-6 | Fomentar que las carnicerías trabajen en regla (incentivos o visibilidad positiva)        | Carnicero             |

---

## 5. Actores del sistema

| Actor           | Descripción                                                            | Acceso                                                     |
| --------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------- |
| Inspector       | Personal de campo del programa PROCAME                                 | Dispositivo móvil, con y sin conexión                      |
| Público general | Consumidor que consulta carnicerías                                    | Web pública, sin autenticación                             |
| Administrador   | Gestiona datos maestros de establecimientos, habilitaciones y usuarios | Web (escritorio)                                           |
| SENASA          | Organismo nacional que otorga los sellos de trazabilidad               | **[PENDIENTE]** — integración a definir                    |
| Establecimiento | Carnicería, matadero o frigorífico                                     | **[PENDIENTE]** — ¿accede el carnicero a cargar sus datos? |

---

## 6. Alcance

### 6.1 Dentro del alcance

- Aplicación **web responsiva** (no APK ni app nativa).
- Autenticación de inspectores con usuario propio.
- Registro geolocalizado de carnicerías habilitadas y mapa provincial.
- Semáforo de estado de habilitación por establecimiento.
- Módulo de inspección en campo con soporte offline.
- Registro de tickets, observaciones y multas con evidencia (foto, GPS, fecha y hora).
- Mapas de calor de infracciones y de establecimientos en regla.
- Consulta pública del estado de cada carnicería.
- Aprovechamiento de la base de datos provincial ya existente como fuente de registro.

### 6.2 Fuera del alcance

- Emisión de habilitaciones oficiales o notificación legal de sanciones (hoy es un trámite del Ministerio).
- Gestión del sistema interno de SENASA.
- Integración con organismos o sistemas de otras provincias sin acuerdo previo.
- App móvil nativa.

---

## 7. Requisitos funcionales

### 7.1 Módulo público

| ID        | Requisito                                                                                                                         | Origen              |
| --------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| RF-PUB-01 | Mostrar en un mapa todas las carnicerías habilitadas de la provincia, con su ubicación                                            | anotaciones_previas |
| RF-PUB-02 | Permitir consultar el estado de habilitación de una carnicería concreta                                                           | anotaciones_previas |
| RF-PUB-03 | Mostrar el semáforo de habilitación por establecimiento: 🟢 Verde = habilitada, 🟡 Amarillo = próxima a vencer, 🔴 Rojo = vencida | anotaciones_previas |
| RF-PUB-04 | Permitir filtrar el mapa por estado, localidad y tipo de especie (vacuno / porcino)                                               | derivado            |

### 7.2 Módulo de inspector

| ID        | Requisito                                                                                     | Origen                 |
| --------- | --------------------------------------------------------------------------------------------- | ---------------------- |
| RF-INS-01 | El inspector debe poder iniciar sesión con su usuario                                         | requerimientos_previos |
| RF-INS-02 | Registrar una inspección de un establecimiento, geolocalizada                                 | derivado               |
| RF-INS-03 | Verificar la presencia y validez de los sellos de trazabilidad en la mercadería **[?]**       | requerimientos_previos |
| RF-INS-04 | Guardar el formulario de inspección **en cualquier momento**, incluso sin conexión a internet | requerimientos_previos |
| RF-INS-05 | Enviar el formulario guardado cuando se recupere la conectividad (sincronización)             | requerimientos_previos |
| RF-INS-06 | Generar una observación o multa cuando detecte faltantes de sellos                            | requerimientos_previos |
| RF-INS-07 | Registrar en la observación: lugar, fecha, hora, foto (si es posible) y posición GPS          | requerimientos_previos |
| RF-INS-08 | Levantar un ticket ante un problema detectado en faenadores o mataderos                       | anotaciones_previas    |
| RF-INS-09 | Consultar el historial de inspecciones y observaciones de un establecimiento                  | derivado               |
| RF-INS-10 | Trabajar sobre interfaz responsiva, pensada para celular                                      | requerimientos_previos |

> **[?] Pendiente de investigación:** funcionamiento de los chips y sellos de trazabilidad, y qué se verifica concretamente en cada punto de control. Si el sellado incluye lectura de chip (RFID), el flujo de captura de datos cambia respecto de una carga manual.

### 7.3 Módulo de administración

| ID        | Requisito                                                                                      | Origen                                       |
| --------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------- |
| RF-ADM-01 | Administrar el padrón de carnicerías habilitadas de la provincia                               | requerimientos_previos                       |
| RF-ADM-02 | Administrar el padrón de mataderos y frigoríficos                                              | requerimientos_previos                       |
| RF-ADM-03 | Cargar y actualizar habilitaciones con sus fechas de emisión y vencimiento (base del semáforo) | anotaciones_previas                          |
| RF-ADM-04 | Administrar usuarios (inspectores) y roles                                                     | derivado                                     |
| RF-ADM-05 | Gestionar la bandeja de observaciones y multas: estado, seguimiento y resolución               | derivado                                     |
| RF-ADM-06 | Generar reportes y las capas de mapas de calor                                                 | requerimientos_previos / anotaciones_previas |

### 7.4 Motor de semáforo

| ID        | Regla                                                                                            |
| --------- | ------------------------------------------------------------------------------------------------ |
| RF-SEM-01 | 🟢 **Verde:** habilitación vigente, dentro del período de validez                                |
| RF-SEM-02 | 🟡 **Amarillo:** habilitación próxima a vencer — **[PENDIENTE: ¿cuántos días de anticipación?]** |
| RF-SEM-03 | 🔴 **Rojo:** habilitación vencida                                                                |

---

## 8. Requisitos no funcionales

| ID     | Requisito                                                                                                                                                             |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RNF-01 | Aplicación **web responsiva**; no se entrega APK                                                                                                                      |
| RNF-02 | **Operación offline obligatoria:** el inspector trabaja en lugares remotos sin internet y no debe perder datos                                                        |
| RNF-03 | Persistencia local del formulario y de las evidencias (foto) mientras no hay red                                                                                      |
| RNF-04 | Geolocalización del dispositivo en el momento de la inspección; sin señal se usa la última posición conocida                                                          |
| RNF-05 | Captura de foto desde la cámara del dispositivo, tolerante a la falta de señal                                                                                        |
| RNF-06 | Toda evidencia queda asociada a su observación: fecha, hora, lugar, GPS y foto                                                                                        |
| RNF-07 | Autenticación de usuarios del Organismo; los datos del expediente son visibles solo para personal autorizado                                                          |
| RNF-08 | Integridad y trazabilidad de cambios: toda modificación de un expediente debe quedar auditada                                                                         |
| RNF-09 | Soporte de mapa provincial completo, con agrupación de marcadores por tratarse de una provincia con muchísimos establecimientos — **[PENDIENTE: definir clustering]** |
| RNF-10 | Interfaz en español, pensada para usuarios no técnicos en campo                                                                                                       |
| RNF-11 | Escalabilidad: la provincia maneja un volumen alto de establecimientos y de inspecciones                                                                              |

---

## 9. Reglas de negocio

1. El circuito de la carne es **ganado → faenador/matadero → carnicería → consumidor**; cada eslabón debe poder verificarse.
2. Las reses que salen de un matadero deben tener **sello de trazabilidad de SENASA** **[? por confirmar]**.
3. En la carnicería se debe **verificar que las reses conserven los sellos de origen**.
4. Ante faltantes de sellos se genera una **observación de multa**, con lugar, fecha, hora, foto y posición GPS.
5. Un establecimiento vencido se marca en **rojo** y deja de ser considerado habilitado a los efectos del semáforo.
6. La habilitación para carne vacuna y la de carne de cerdo pueden tener requisitos y vigencias distintas **[?]**.

---

## 10. Flujos principales

### 10.1 Inspección en campo (caso habitual, sin señal)

```
Inspector inicia sesión
   → Selecciona establecimiento (padrón ya sincronizado)
   → Completa el formulario de inspección
   → [GUARDAR]           → se persiste en el dispositivo (funciona sin internet)
   → [GUARDAR Y ENVIAR]  → se persiste y, si hay red, se envía al servidor
   → Al recuperar conectividad se sincronizan automáticamente los pendientes
```

### 10.2 Detección de infracción

```
Inspector detecta faltante de sellos
   → Levanta el ticket / observación de multa
   → El sistema captura fecha, hora, GPS y foto (si es posible)
   → Se guarda (online u offline)
   → Queda en la bandeja del Administrador para su seguimiento
```

### 10.3 Consulta pública

```
Ciudadano entra al sitio
   → Ve el mapa provincial con todas las carnicerías
   → Filtra o busca una carnicería
   → Consulta su semáforo de habilitación
```

---

## 11. Modelo de datos inicial

Entidades tentativas, a validar en la etapa de diseño.

| Entidad             | Campos principales                                                                                                                     |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Usuario             | id, nombre, usuario, hash de contraseña, rol, activo                                                                                   |
| Establecimiento     | id, tipo (carnicería / matadero / frigorífico), razón social, CUIT, dirección, latitud, longitud, localidad, teléfono, especie         |
| Habilitación        | id, establecimiento, especie, número, fecha de emisión, fecha de vencimiento, estado                                                   |
| Inspección          | id, inspector, establecimiento, fecha y hora, latitud, longitud, resultado, enviada                                                    |
| Sello verificado    | id, inspección, tipo de corte, número de sello, estado (presente / faltante / vencido / ilegible) **[? según investigación de chips]** |
| Observación o multa | id, inspección, tipo, descripción, estado, resolución — **[PENDIENTE: flujo de sanción]**                                              |
| Evidencia           | id, observación, archivo, fecha y hora, latitud, longitud                                                                              |
| Auditoría           | id, usuario, acción, entidad, fecha y hora                                                                                             |

---

## 12. Riesgos identificados

| #   | Riesgo                                                           | Impacto | Mitigación                                                        |
| --- | ---------------------------------------------------------------- | ------- | ----------------------------------------------------------------- |
| 1   | Zona rural sin señal                                             | Alto    | Diseño offline-first como requisito central (RNF-02)              |
| 2   | Requisitos de trazabilidad todavía sin entender (chips y sellos) | Alto    | Investigación obligatoria antes de diseñar el formulario          |
| 3   | Base de datos de origen en formato desconocido                   | Medio   | Relevamiento de la base actual en la próxima reunión              |
| 4   | Geolocalización no disponible o imprecisa                        | Medio   | El GPS queda como dato complementario, nunca como única evidencia |
| 5   | Fotos pesadas con mala conexión                                  | Medio   | Compresión y carga diferida de evidencias                         |
| 6   | Crecimiento del alcance (incentivos, heatmaps, SENASA)           | Medio   | Priorización con la referente en la próxima reunión               |
| 7   | Uso indebido o difusión de los datos de inspección               | Legal   | Restricción a inspectores autorizados y auditoría de accesos      |

---

## 13. Investigación pendiente

- [ ] Rol y funcionamiento de **SENASA** en el proceso.
- [ ] Funcionamiento de **chips y sellos** de trazabilidad: ¿RFID, impresión, código?
- [ ] Descripción detallada del circuito: ganado → faenador → carnicerías.
- [ ] Requisitos de habilitación de una carnicería para vender **carne vacuna** y para **carne de cerdo**.
- [ ] Formato, calidad y cobertura de la base de datos existente de carnicerías y productores.
- [ ] Procedimiento formal de sanción por observación o multa.

---

## 14. Preguntas abiertas para la Ing. Julia Luna

1. ¿Cuál es la prioridad real: la herramienta del inspector, el portal del público, o ambos?
2. ¿El sistema debe limitarse a consultar carnicerías o también gestionar el trámite de habilitación?
3. ¿Cuánto tiempo se considera "próxima a vencer" para el semáforo amarillo?
4. ¿Qué incentivos están previstos para las carnicerías en regla? El mecanismo concreto está sin definir.
5. ¿Los mapas de calor son de infracciones, de carnicerías en regla, o de "mejor valoradas"? La anotación menciona los tres y son objetivos distintos.
6. ¿Existe integración posible con SENASA o el vínculo es puramente documental (foto del sello)?
7. ¿El inspector trabaja offline en un dispositivo asignado por el Organismo o en su propio celular? Esto condiciona toda la arquitectura offline.
8. ¿Quién carga y mantiene las habilitaciones: el Administrador del Ministerio o se importan de otro sistema?

---

## 15. Próximo paso

Reunión de validación con la Ing. Julia Luna para:

1. Confirmar el alcance y responder las preguntas abiertas.
2. Acordar los datos de origen disponibles.
3. Cerrar la investigación pendiente sobre SENASA, chips y sellos.
4. Definir las prioridades del primer incremento.

---

## 16. Glosario

| Término               | Definición                                                    |
| --------------------- | ------------------------------------------------------------- |
| PROCAME               | Programa provincial de control de carnicerías habilitadas     |
| SENASA                | Servicio Nacional de Sanidad y Calidad Agroalimentaria        |
| Faenador / Matadero   | Establecimiento donde se realiza el faenado de las reses      |
| Frigorífico           | Establecimiento que procesa, conserva y despacha carne        |
| Sello de trazabilidad | Identificación oficial del origen de la res                   |
| Habilitación          | Autorización para operar como establecimiento habilitado      |
| Observación de multa  | Registro formal de una infracción detectada en una inspección |

---

## 17. Trazabilidad con las fuentes

| Sección de este documento    | `requerimientos_previos.md` | `anotaciones_previas.md` |
| ---------------------------- | --------------------------- | ------------------------ |
| §2 Contexto institucional    | líneas 1–4                  | líneas 1–2               |
| §3 Problemática              | líneas 7–8                  | líneas 12–13             |
| §4 Objetivos                 | líneas 6–8                  | líneas 15–25             |
| §6 Alcance                   | líneas 11, 17               | líneas 17–25             |
| §7 Requisitos funcionales    | líneas 13–18                | líneas 17–24             |
| §8 Requisitos no funcionales | líneas 12, 15–18            | línea 18                 |
| §9 Reglas de negocio         | líneas 7, 13–14             | líneas 5–10              |
| §10 Flujos                   | líneas 15–18                | línea 23                 |
| §13 Investigación pendiente  | línea 13                    | líneas 4–10              |
| §14 Preguntas abiertas       | línea 15                    | líneas 27–28             |

