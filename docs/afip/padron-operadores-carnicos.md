# Padrón de Operadores Cárnicos — AFIP

> Estructura del padrón de operadores cárnicos publicado por AFIP (Actividades Agropecuarias).

## Estructura de campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `CUIT` | numérico (11 dígitos) | Código Único de Identificación Tributaria del operador |
| `Razon_Social` | texto | Razón social / nombre del operador |
| `Categoria` | texto | Categoría del operador (ver [Categorías](#categorías)) |
| `Situacion` | texto | Situación en el padrón (ej. `EXCLUIDO`) |
| `Desde fecha` | fecha (d/m/a) | Fecha de inicio de la situación |
| `Hasta fecha` | fecha (d/m/a) | Fecha de fin de la situación (vacío si vigente) |
| `CBU` | numérico (22 dígitos) | Cuenta Bancaria Universal |
| `Fecha actualizaciøn CBU` | fecha (d/m/aa) | Fecha de actualización del CBU |

## Categorías

### Categoría bovina / bubalina

| Categoría |
|-----------|
| Productor/criador |
| Matarifes abastecedores y carniceros y otros usuarios de faena |
| Feed lots |
| Invernador |
| Comercializadores de subproductos |
| Establecimientos faenadores y/o frigorífico |
| Consignatario de Carnes |
| Consignatarios y/o comisionistas de Hacienda |
| Adquirentes de cueros crudos (frescos y salados) |
| Mercado concentradores/feria/predios feriales |
| Consignatarios directos |

### Categoría porcina

| Categoría |
|-----------|
| Productores/Criadores Comerciales |
| Invernadores |
| Matadero - Frigorífico |
| Matarifes - Abastecedores y carniceros - y toda otra modalidad de usuarios de faena |
| Consignatario y/o comisionistas de carnes |
| Ferias o Predios Feriales de Comercialización de hacienda |
| Consignatarios y/o comisionistas de hacienda |
| Consignatarios directos de hacienda |

## Ejemplo de datos

```csv
CUIT    Razon_Social    Categoria    Situacion    Desde fecha    Hasta fecha    CBU    Fecha actualizaciøn CBU
20002732492    SUCESION DE ENCISO EMILIO FRANCISCO    Productor/criador    EXCLUIDO    12/5/22        0110361620036100347321    17/9/20
20003535542    SUCESION DE ARANCET GASTON GERARDO    Productor/criador    EXCLUIDO    15/11/21
```

### Como tabla

| CUIT | Razon_Social | Categoria | Situacion | Desde fecha | Hasta fecha | CBU | Fecha actualizaciøn CBU |
|------|--------------|-----------|-----------|-------------|-------------|-----|--------------------------|
| 20002732492 | SUCESION DE ENCISO EMILIO FRANCISCO | Productor/criador | EXCLUIDO | 12/5/22 | | 0110361620036100347321 | 17/9/20 |
| 20003535542 | SUCESION DE ARANCET GASTON GERARDO | Productor/criador | EXCLUIDO | 15/11/21 | | | |

## Observaciones

- El separador del archivo es **tabulador** (TSV).
- Los campos pueden quedar **vacíos** (ej. `Hasta fecha` y `Fecha actualizaciøn CBU` en el segundo registro).
- El nombre del campo `Fecha actualizaciøn CBU` conserva el acento invertido (`ø`) del encabezado original.
