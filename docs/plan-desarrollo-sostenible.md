# Plan de Desarrollo Sostenible de la APP ROCCA (ProCarne)

> **Proyecto:** ROCCA — Registro de Operadores y Control de la Cadena Cárnica de Santiago del Estero
> **Stack actual:** FastAPI + SQLAlchemy 2.0 + Uvicorn (backend), Vite + React (frontend), SQLite en desarrollo / PostgreSQL en producción.
> **Marco de referencia:** Green Software Foundation (principios L1–L4 y métrica SCI — Software Carbon Intensity), ISO 14001:2015, ISO/IEC 25010 (eficiencia del rendimiento), CMMI-Green (mejora continua).

---

## 1. Objetivos y lineamientos

El plan aplica los cuatro principios de sostenibilidad del software a lo largo de todo el ciclo de vida de ROCCA:

| Principio | Aplicación concreta en ROCCA |
| --- | --- |
| **Eficiencia energética** | Minimizar consumo en ejecución: caché de consultas frecuentes (operadores verificados, categorías), paginación en todas las listados, operación offline del inspector para evitar reenvíos. |
| **Eficiencia de hardware** | No sobredimensionar: un único servicio FastAPI multi-worker dimensionado por carga real; PostgreSQL sin réplicas innecesarias en la primera fase; contenedores con límites de CPU/memoria. |
| **Optimización del código** | Reducir operaciones innecesarias, uso de CPU y memoria: índices en las consultas de trazabilidad, evitar N+1 en los DAO, serialización parcial de respuestas. |
| **Mantenimiento sostenible** | Extender la vida útil del sistema: modularidad por módulos I–VII, tests automatizados (pytest), migraciones Alembic versionadas, evitar reescrituras tempranas. |

Cada etapa del ciclo genera impacto ambiental: en **desarrollo** se optimiza compilación/testing (tests en SQLite en memoria, sin imágenes pesadas de CI); en **operación** se prioriza infraestructura con energía de baja intensidad de carbono; en **mantenimiento** se evita el desarrollo redundante.

## 2. Métricas de eficiencia energética y huella de carbono digital

Se instrumentan tres KPIs, medidos por sprint y reportados en un tablero de sostenibilidad (módulo VII — información estratégica):

| Métrica | Fórmula | Herramienta |
| --- | --- | --- |
| Consumo energético por usuario | `E_total / usuarios_activos` (kWh/usuario/mes) | Telemetry API + contador de usuarios activos |
| **CO₂/request** | `E_por_solicitud (kWh) × factor_carbono_red (kg CO₂e/kWh)` | Telemetry API + factor de red (ADEE / base regional) |
| **CPU y memoria por línea de código** | `tiempo_CPU (s) / LOC_ejecutadas` y `pico_memoria (MB) / LOC_ejecutadas` | cProfile + tracemalloc + cobertura de líneas (pytest-cov) |

**Lineas base (fase 1):** se mide la versión inicial de cada endpoint para establecer el baseline; las metas se definen como reducciones porcentuales sobre ese baseline (p. ej. −20 % CO₂/request al cierre del incremento 2).

---

## 3. Reducción del consumo energético por usuario

El consumo por usuario (`E/usuario`) se reduce atacando los tres componentes del gasto:

1. **Energía de servidor por interacción del usuario** (componente dominante):
   - **Caché de lecturas calientes:** los endpoints de consulta pública (operadores verificados, por categoría y localidad) se cachean (Redis o caché in-process con TTL corto). Un inspector que consulta la misma carnicería 10 veces al día consume energía solo la primera vez.
   - **Paginación y filtros en base de datos:** ningún listado se devuelve completo; la paginación limita el trabajo de CPU/DB por solicitud.
   - **Operación offline del inspector (módulo de campo):** el formulario offline sincroniza por lotes en lugar de solicitar por cada acción, reduciendo el número de round-trips (cada round-trip = energía de red + servidor + dispositivo).
   - **Respuestas parciales (fieldsets):** los endpoints devuelven solo los campos que consume cada vista (lista vs. detalle), reduciendo serialización, memoria y ancho de banda.
2. **Energía del dispositivo del usuario:**
   - Frontend Vite con code-splitting por rol (inspector / administrador / público), bundle mínimo para el dispositivo móvil de campo (batería = energía).
   - Imágenes y sellos de trazabilidad en formatos optimizados (WebP, dimensiones acotadas).
3. **Energía de la red:**
   - Compresión gzip/brotli, HTTP/2, y sincronización delta (solo cambios) en la app offline.

**Meta medible:** reducir `E/usuario` ≥ 20 % contra el baseline al cierre del incremento 2, verificable con la Telemetry API (muestreo de energía de servidor) dividida por usuarios activos del mes.

## 4. Medición del CO₂ generado por cada solicitud (CO₂/request)

Se adopta el enfoque de la **Green Software Foundation (métrica SCI)**:

```
CO₂/request = E_request (kWh) × F_red (kg CO₂e/kWh)
```

**Paso 1 — Medir la energía por solicitud (E_request):**
- Instrumentar el backend con **Telemetry API** (`telemetry-api` del Green Software Foundation): un middleware de FastAPI mide el consumo energético del proceso (CPU, RAM, disco, red) por request y lo convierte a kWh usando la potencia nominal de la infraestructura.
- Alternativa complementaria (bajo costo): medir `tiempo_CPU × P_CPU + memoria_tocada × P_RAM` por request y promediar por endpoint.
- En producción, cruzar con la **factura energética real del servidor/VM** (`E_servidor / total_requests`) para calibrar el muestreo.

**Paso 2 — Aplicar el factor de carbono de la red (F_red):**
- Usar el factor de intensidad de carbono de la red eléctrica argentina/región (kg CO₂e/kWh, fuente ADEE o el proveedor de la infraestructura) y actualizarlo anualmente.
- Registrar el **CO₂e por endpoint** (p. ej. `GET /operadores` vs. `POST /trazabilidad`), no solo el promedio global: esto identifica qué flujos de los módulos I–VII emiten más.

**Paso 3 — Cerrar el ciclo de mejora (CMMI-Green):**
- Reportar `CO₂/request` global y por endpoint en el tablero de sostenibilidad (módulo VII).
- **Programar por intensidad de carbono:** los procesos no urgentes (informes estadísticos, respaldos, sincronización masiva de trazabilidad) se ejecutan por lotes en horarios de menor intensidad de carbono de la red.
- Meta: `CO₂/request` ≤ valor de baseline × 0,8 al cierre del incremento 2, con reporte mensual.

## 5. Eficiencia de CPU y memoria por línea de código

**Definición de la métrica:**

```
eficiencia_CPU  = tiempo_CPU_total (s)  / líneas_de_código_ejecutadas
eficiencia_MEM  = pico_memoria (MB)     / líneas_de_código_ejecutadas
```

**Cómo se mide:**
1. **Cobertura de líneas (denominador):** `pytest-cov` sobre la suite de tests (pytest + SQLite en memoria, ya existente en `src/backend`) da las líneas ejecutadas por módulo y por test.
2. **CPU (numerador 1):** `cProfile`/`py-spy` sobre la suite de tests y sobre el benchmark de endpoints (locust/k6) da el tiempo de CPU por test/endpoint.
3. **Memoria (numerador 2):** `tracemalloc` (picos de asignación por test) y RSS del proceso bajo carga.
4. **Cálculo por módulo:** la suite se ejecuta módulo por módulo (los DAOs de `src/backend/app/modulos` ya están separados), de modo que cada módulo reporta su `s/línea` y `MB/línea` — esto localiza el código ineficiente, no solo el promedio del sistema.

**Cómo se mejora (optimización del código):**
- **Eliminar operaciones innecesarias:** refactor de los DAOs para evitar consultas N+1 en la trazabilidad (un join en lugar de N consultas); índices en `operador`, `fecha` y `documento` para que las búsquedas de fiscalización toquen pocas filas (el ejemplo del catálogo: de 5 s a 1 s por búsqueda).
- **Reducir picos de memoria:** paginación en el cursor de la DB (SQLAlchemy `yield_per`), streaming de los reportes de información estratégica en lugar de cargarlos en memoria, y serialización parcial de respuestas.
- **Benchmark en CI:** un job de CI ejecuta la suite con profiling y **falla el pipeline si el ratio CPU/línea o MEM/línea de un módulo crece más del 10 %** contra la baseline (regresión de eficiencia bloquea el merge, igual que una regresión de funcionalidad).
- **Mantenimiento sostenible:** el ratio también se usa para decidir refactorizaciones preventivas (código duplicado, librerías obsoletas) antes de que degraden el rendimiento.

**Meta medible:** `CPU/línea` y `MEM/línea` no degradarse más del 10 % entre incrementos, y reducir ≥ 15 % en los módulos con peor ratio al cierre del incremento 2.

## 6. Plan de ejecución por incrementos

| Incremento | Acciones de sostenibilidad | Entregables |
| --- | --- | --- |
| **1 — Baseline** | Instrumentar Telemetry API + cProfile/tracemalloc/pytest-cov; medir baseline de las 3 métricas por endpoint y módulo. | Dashboard de baseline; job de profiling en CI. |
| **2 — Optimización** | Caché de consultas calientes, paginación, índices, fix de N+1, fieldsets, code-splitting frontend, programación por intensidad de carbono de los lotes. | −20 % CO₂/request, −20 % E/usuario, −15 % en los peores ratios CPU/MEM por línea. |
| **3 — Institucionalización** | Reporte mensual de huella de carbono digital en el módulo VII; metas por incremento en el plan de mantenimiento; política de no degradar eficiencia en CI. | Reporte de sostenibilidad; política de mantenimiento sostenible (extender vida útil, evitar reemplazos tempranos). |

## 7. Referencias (catálogo ingeniería-de-software)

- Green Software Foundation — Software Carbon Intensity (SCI) y programación por intensidad de carbono.
- ISO 14001:2015 — Gestión ambiental de la organización (política de consumo eléctrico de servidores).
- ISO/IEC 25010 — Eficiencia del rendimiento como característica de calidad del software.
- CMMI-Green — Integración de criterios ambientales en planificación, desarrollo, evaluación y mejora continua.
- Principios de sostenibilidad en el software: eficiencia energética, eficiencia de hardware, optimización del código, mantenimiento sostenible.
