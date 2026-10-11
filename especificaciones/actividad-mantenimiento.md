# Actividad: Mantenimiento de mi Software (PP1 — ROCCA/ProCarne)

> Software en desarrollo: **ROCCA** — Registro de Operadores y Control de la Cadena Cárnica de Santiago del Estero.
> Fuente de requisitos: `especificaciones/especificaciones.md` y `trabajo-practico.md` (secciones 2.1 y 2.3).

---

## 1. Requisitos funcionales (2)

| ID | Requisito | Descripción |
| --- | --- | --- |
| **RF-FIS-01** | Registrar inspecciones de establecimientos, geolocalizadas | El inspector completa el formulario de inspección de un establecimiento (padrón sincronizado), con captura de fecha, hora, posición GPS y resultado de la visita. (Módulo III — Fiscalización) |
| **RF-PUB-01** | Mostrar en un mapa provincial todos los operadores verificados, con su ubicación | El portal público expone el mapa provincial con los operadores registrados, su semáforo de habilitación (🟢 vigente / 🟡 próxima a vencer / 🔴 vencida) y filtros por estado, localidad, tipo de operador y especie. (Módulo V — Portal Público) |

## 2. Requisitos no funcionales (2)

| ID | Requisito | Categoría |
| --- | --- | --- |
| **RNF-02** | Operación offline obligatoria: el inspector trabaja en lugares remotos sin internet y no debe perder datos; el formulario y las evidencias se persisten localmente y se sincronizan al recuperar conectividad. | Confiabilidad |
| **RNF-07** | Autenticación de usuarios del Organismo: los datos del expediente son visibles solo para personal autorizado; toda modificación queda auditada. | Seguridad |

## 3. Diagrama de Casos de Uso

Ver [`diagramas/casos-de-uso.drawio`](diagramas/casos-de-uso.drawio) (abrir con draw.io / diagrams.net).

| Actor | Casos de uso |
| --- | --- |
| Inspector | CU-01 Iniciar sesión · CU-02 Registrar inspección · CU-03 Guardar inspección offline · CU-04 Sincronizar inspecciones · CU-05 Generar observación/multa · CU-06 Consultar historial |
| Operador | CU-07 Declarar movimiento comercial · CU-08 Confirmar recepción · CU-09 Consultar estado |
| Administrador | CU-10 Gestionar padrón · CU-11 Gestionar habilitaciones · CU-12 Gestionar usuarios · CU-13 Gestionar bandeja de fiscalización · CU-14 Generar reportes |
| Público general | CU-15 Consultar mapa de operadores · CU-16 Filtrar operadores · CU-17 Consultar estado de operador |

Relaciones `<<include>>`: CU-02 → CU-03 → CU-04; CU-05 → CU-03; CU-07 → CU-08; CU-16 → CU-17.

## 4. Herramientas de desarrollo

| Capa | Herramienta |
| --- | --- |
| IDE | **Visual Studio Code** |
| Diseño de UI / wireframes | **Figma** |
| Diagramas (casos de uso, contexto, arquitectura, ER) | **draw.io (diagrams.net)** |
| Frontend | **TypeScript** (PWA responsiva, offline-first) |
| Backend | **Java** (API REST, Spring Boot) |
| Base de datos | **PostgreSQL** |
| Deploy a la nube | **Oracle Cloud** (OCI) |
| Control de versiones | **Git** (GitHub) |

## 5. Actividades de mantenimiento del software (10)

| # | Actividad | Descripción |
| --- | --- | --- |
| 1 | **Corrección de defectos** | Recibir, registrar y corregir errores reportados por inspectores y administradores (ej. fallo en la sincronización offline), con verificación y cierre del ticket. |
| 2 | **Adaptación a nuevos navegadores/dispositivos** | Ajustar la PWA responsiva ante nuevas versiones de navegadores móviles o cambios en las APIs de geolocalización/cámara usadas en inspección. |
| 3 | **Migraciones y mantenimiento de la base de datos** | Aplicar migraciones de esquema PostgreSQL (nuevas columnas en Operador, Movimiento Comercial, etc.), respaldos (backups) y monitoreo de rendimiento. |
| 4 | **Actualización del motor de semáforo** | Ajustar la regla de "próxima a vencer" (🟡) cuando se defina el umbral de días pendiente (RF-SEM-02), y validar el cambio en datos reales. |
| 5 | **Mantenimiento de la integración con organismos nacionales** | Adaptar el módulo de trazabilidad a los cambios en los formatos de DTE/REC (ARCA) y DUT (Senasa), o a la definición del escenario de integración (API vs. referencia documental). |
| 6 | **Actualización de dependencias y parches de seguridad** | Revisar y actualizar dependencias del backend Java y del frontend, aplicando parches de seguridad (autenticación JWT, exposición del portal público). |
| 7 | **Mejora de rendimiento del mapa provincial** | Optimizar el clustering de marcadores y las consultas de geolocalización ante el crecimiento del padrón de operadores (RNF-09, RNF-11). |
| 8 | **Mantenimiento de la funcionalidad offline** | Validar y corregir la persistencia local (IndexedDB) y el mecanismo de sincronización tras pérdida de red o reinicio del dispositivo. |
| 9 | **Actualización del padrón inicial** | Reimportar y limpiar los datos de la base de datos provincial existente cuando se disponga de versiones actualizadas (formato, calidad, cobertura). |
| 10 | **Monitoreo y despliegue en Oracle Cloud** | Monitorear disponibilidad, logs y métricas del servicio desplegado en OCI; ejecutar despliegues de nuevas versiones y regresiones ante incidentes. |
