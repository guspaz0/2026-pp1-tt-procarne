-- Datos iniciales: Categorías por actividad (RFOCB)
-- Fuente: Normativa AFIP — Registro Federal de Operadores del Comercio de Hacienda

-- Actividades
INSERT OR IGNORE INTO actividades (id, nombre) VALUES (1, 'Bovino/Bubalino');
INSERT OR IGNORE INTO actividades (id, nombre) VALUES (2, 'Porcino');

-- Categorías: Bovino/Bubalino (actividad_id = 1)
INSERT OR IGNORE INTO categorias_afip (actividad_id, codigo, descripcion) VALUES
    (1, 'B1', 'Productor/criador'),
    (1, 'B2', 'Matarifes abastecedores y carniceros y otros usuarios de faena'),
    (1, 'B3', 'Feed lots'),
    (1, 'B4', 'Invernador'),
    (1, 'B5', 'Comercializadores de subproductos'),
    (1, 'B6', 'Establecimientos faenadores y/o frigorífico'),
    (1, 'B7', 'Consignatario de Carnes'),
    (1, 'B8', 'Consignatarios y/o comisionistas de Hacienda'),
    (1, 'B9', 'Adquirentes de cueros crudos (frescos y salados)'),
    (1, 'B10', 'Mercado concentradores/feria/predios feriales'),
    (1, 'B11', 'Consignatarios directos');

-- Categorías: Porcino (actividad_id = 2)
INSERT OR IGNORE INTO categorias_afip (actividad_id, codigo, descripcion) VALUES
    (2, 'P1', 'Productores/Criadores Comerciales'),
    (2, 'P2', 'Invernadores'),
    (2, 'P3', 'Matadero - Frigorífico'),
    (2, 'P4', 'Matarifes - Abastecedores y carniceros - y toda otra modalidad de usuarios de faena'),
    (2, 'P5', 'Consignatario y/o comisionistas de carnes'),
    (2, 'P6', 'Ferias o Predios Feriales de Comercialización de hacienda'),
    (2, 'P7', 'Consignatarios y/o comisionistas de hacienda'),
    (2, 'P8', 'Consignatarios directos de hacienda');
