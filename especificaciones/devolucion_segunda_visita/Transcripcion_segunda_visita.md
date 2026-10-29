# ROCCA: cómo se implementa sin duplicar SENASA ni ARCA

## Resumen

El ROCCA registra a cada operador una sola vez y se alimenta de lo que ARCA y SENASA ya generan en cada movimiento de carne, de modo que la provincia controla sin pedir papeles nuevos. Lo que aporta la provincia es lo que ninguna base nacional tiene: la identidad provincial del operador, el cruce entre quien envía y quien recibe, y las alertas para controlar en el territorio.

Cuatro reglas de diseño sostienen toda la propuesta:

1. Nada que ya conste en ARCA o SENASA se vuelve a pedir ni a cargar.
2. El operador carga datos propios solo cuando no existe fuente nacional: carne de especies que el Remito Electrónico Cárnico no cubre (caprino, ovino, aves y otras) y su habilitación provincial.
3. La Constancia Provincial de Circulación Cárnica (CPCC) se genera sola a partir del remito electrónico. No es un trámite, no es un documento de transporte y no se suma a los papeles que lleva el camión.
4. El operador que cumple no hace nada más de lo que ya hace con ARCA y SENASA, y recibe beneficios. El que no cumple queda visible.

Una condición: que la carga sea cero para el operador depende de que la provincia pueda consultar los datos del remito electrónico. Eso requiere un convenio con ARCA; la sección 9 explica cómo hacerlo y qué plan B existe si se demora.

## 1. Cómo trabaja hoy la cadena de la carne

Hoy cada movimiento de carne ya deja rastro digital en tres puntos: SENASA registra el animal y la faena, ARCA registra el traslado y la recepción de la carne, y los registros de operadores identifican quién es quién. La provincia no necesita crear un cuarto sistema: necesita acceso a estos tres.

| Sistema | Qué registra | Quién lo carga hoy |
|---|---|---|
| DT-e (SENASA, SIGSA) | Traslado de animales a faena. El frigorífico debe cerrarlo al ingreso, en SIGICA o en el sistema equivalente de los establecimientos provinciales y municipales | Productor o autogestor lo emite; el frigorífico lo cierra |
| Sistema Integral de Faena (Res. 586/2015) | Ingreso de hacienda, autorización de faena, resultado de faena y decomisos. El libro de movimiento de carne en papel se eliminó (Res. 40/2026) y quedó integrado en SIF/SIGICA | El establecimiento faenador |
| Remito Electrónico Cárnico, REC (ARCA, RG 4256/2018) | Traslado de carne y subproductos bovinos, bubalinos y porcinos. Es el único documento válido para el traslado automotor | Lo emiten frigoríficos, usuarios de faena, abastecedores, desposteros y consignatarios |
| Aceptación del REC (ARCA) | El destinatario acepta o rechaza la mercadería, por la web o por la app leyendo el QR del remito. Con 5 remitos vencidos sin aceptar o rechazar, los emisores ya no pueden emitirle más | El receptor (carnicería, frigorífico, etc.) |
| Vinculación REC con factura (RG 5259/2022) | El número de REC figura en la factura electrónica de venta de la carne | El vendedor |
| SIOCAL (SAGyP) | Registro de operadores de la cadena de ganados y carnes. Reemplazó al RUCA, eliminado por Res. 50/2025 | El operador, una vez |
| ROC provincial | Habilitación con troquel anual, inspección ocular y tasa de Rentas. No ve el flujo de mercadería | El operador, ante ProCarne |

Tres consecuencias para el diseño:

- El REC es la columna vertebral: tiene emisor, destinatario, producto y la confirmación de recepción. Todo lo que la provincia necesita saber de un movimiento está ahí.
- El REC cubre solo bovino, bubalino y porcino. Caprino, ovino, aves y otras especies circulan sin un remito nacional equivalente; ahí sí hay un vacío que la provincia puede llenar.
- La política nacional va hacia menos registros y menos duplicación (por eso desapareció el RUCA y se unificó el libro de movimientos). Una propuesta provincial que duplique pedidos choca con esa línea; una que reutilice datos encaja con ella. (que es lo q se busca con esto)

## 2. Qué hace el ROCCA y qué no

El ROCCA no recibe documentos que ya existen: los consulta. Esta tabla fija, dato por dato, de dónde sale y si el operador tiene que cargarlo.

| Dato | Fuente | ¿Lo carga el operador? |
|---|---|---|
| Emisor, destinatario, producto, cantidades y fecha del traslado | REC (ARCA) | No |
| Aceptación o rechazo de la mercadería | Conformidad del destinatario en ARCA | No, ya lo hace |
| Origen del animal y datos de faena | DT-e y SIF/SIGICA (SENASA) | No |
| Habilitación nacional del frigorífico o despostadero | SENASA / SIOCAL | No, se verifica |
| CUIT y situación fiscal | ARCA | No, se valida |
| Habilitación provincial: solicitud, inspección, troquel, tasa de Rentas | ROCCA y boleta electrónica de Rentas | Sí, lo que presenta hoy pero online y una sola vez |
| Carne de especies sin REC | No hay fuente nacional | Sí, declaración simplificada |

Con las bases nacionales solas, la provincia no ve (salvo que se lo habilite un convenio):

- qué carne entra a la provincia desde otras jurisdicciones y quién la recibe;
- quién recibe carne sin estar registrado ante la provincia;
- qué carne de especies sin REC circula y entre quiénes;
- cuánto se faena en la provincia frente a cuánto se introduce, y qué productores faenan dónde.

Esa es la brecha que cubre el ROCCA, y solo esa.

## 3. Arquitectura: identidad propia, datos de terceros

El ROCCA se arma en tres capas, y la clave que une todo es el CUIT del operador más el Código de Remito Electrónico (CRE) que ARCA asigna a cada REC.

1. **Identidad (propia).** Una ficha única por operador: CUIT validado contra ARCA, tipo de operador, establecimientos, habilitación provincial con su troquel y vencimiento, número de SENASA o SIOCAL si corresponde (se verifica, no se sube) y estado (habilitado, cumplidor, suspendido). Se alimenta del trámite digital de inscripción ya definido, con la boleta de Rentas que genera el propio operador.
2. **Datos de terceros (se consultan).** REC y su aceptación (ARCA), DT-e y faena (SENASA), matrícula de operadores (SIOCAL). El ROCCA guarda solo lo necesario para controlar: CRE, CUIT de emisor y receptor, producto, kilos, fechas y estado. No copia facturas ni documentos, y no guarda importes.
3. **Control (propia).** Cruces y alertas, emisión de la CPCC con su QR, ~~portal público de operadores habilitados~~ y tablero para las oficinas provinciales.

Cada dato vive en un solo lugar. Si ARCA o SENASA lo corrigen, el ROCCA lo ve corregido, porque lo consulta en vez de copiarlo.

## 4. Vínculo con los frigoríficos

Un frigorífico no carga nada nuevo en el ROCCA: el ROCCA usa lo que el frigorífico ya carga en ARCA y en SENASA. La única excepción son los envíos de especies que el REC no cubre.

| Tipo de establecimiento | Lo que ya hace | Qué toma el ROCCA | Qué carga en el ROCCA |
|---|---|---|---|
| Faenador con habilitación SENASA, de la provincia o de otra | Emite el REC por cada traslado y cierra el DT-e en SIGICA | Los REC con destinatario en Santiago del Estero y, por convenio, los datos de faena | Nada. Se lo reconoce por CUIT; la adhesión como Origen Aliado es voluntaria |
| Faenador provincial o municipal de Santiago del Estero | Emite el REC (bovino y porcino) y cierra el DT-e en el sistema provincial o municipal | Los REC y los datos de faena de su propio sistema, que la provincia ya controla como autoridad de aplicación | Nada, mientras use los sistemas vigentes |
| Despostadero, abastecedor, consignatario | Emite el REC cuando traslada | Los REC | Nada |
| Establecimiento de especies sin REC (caprino, ovino, aves, otras) | No existe remito nacional equivalente | Nada, no hay fuente | Declaración simplificada por envío (sección 5) |

De las bases de faena el ROCCA necesita solo tres datos por tropa: el RENSPA del productor, el establecimiento faenador y los kilos faenados. Con eso se responde la pregunta de la propuesta (qué productores faenan dónde y cuánto) sin pedir nada al productor ni al frigorífico.

Regla de oro del vínculo: un frigorífico nunca carga dos veces el mismo dato. Si un dato falta en la fuente nacional, se corrige en la fuente, no con un formulario provincial.

La categoría Origen Aliado ROCCA, voluntaria, sirve para dos cosas: que sus clientes santiagueños vean en el portal que compran a un origen verificado, y que el frigorífico reciba aviso cuando un destinatario suyo tenga remitos vencidos sin aceptar.
