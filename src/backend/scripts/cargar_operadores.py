#!/usr/bin/env python3
"""
Script para cargar datos de operadores en la base de datos de Insforge.

Proceso:
1. Parsear los datos del archivo de texto
2. Insertar personas (si no existen)
3. Insertar operadores (si no existen)
4. Insertar inscripciones con actividades económicas

Uso:
    export ROCCA_DATABASE_URL="postgresql://..."
    python scripts/cargar_operadores.py datos_operadores.txt
"""

from __future__ import annotations

import os
import sys
import re
from datetime import datetime
from typing import Optional
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


def parsear_datos(ruta_archivo: str) -> list[dict]:
    """Parsea el archivo de texto y devuelve una lista de diccionarios con los datos."""
    datos = []
    
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    
    # Saltar la primera línea (encabezados)
    for linea in lineas[1:]:
        linea = linea.strip()
        if not linea:
            continue
        
        # Dividir por tabs
        campos = linea.split('\t')
        if len(campos) < 9:
            continue
        
        # Extraer datos
        cuit = campos[0].strip() if campos[0].strip() else None
        nombre_propietario = campos[1].strip() if len(campos) > 1 and campos[1].strip() else None
        nombre_establecimiento = campos[2].strip() if len(campos) > 2 and campos[2].strip() else None
        localidad = campos[3].strip() if len(campos) > 3 and campos[3].strip() else None
        departamento = campos[4].strip() if len(campos) > 4 and campos[4].strip() else None
        direccion = campos[5].strip() if len(campos) > 5 and campos[5].strip() else None
        fecha_inscripcion_operador = campos[6].strip() if len(campos) > 6 and campos[6].strip() else None
        tipo_carne = campos[7].strip() if len(campos) > 7 and campos[7].strip() else None
        fecha_inscripcion = campos[8].strip() if len(campos) > 8 and campos[8].strip() else None
        
        # Normalizar CUIT (agregar guiones si no tiene)
        if cuit and not re.match(r'^\d{2}-\d{8}-\d$', cuit):
            # Intentar normalizar
            cuit_digits = re.sub(r'[^0-9]', '', cuit)
            if len(cuit_digits) == 11:
                cuit = f"{cuit_digits[:2]}-{cuit_digits[2:10]}-{cuit_digits[10]}"
            elif len(cuit_digits) == 8:
                # DNI, no CUIT
                cuit = cuit_digits
        
        # Normalizar fechas
        def normalizar_fecha(fecha: str) -> Optional[datetime]:
            if not fecha:
                return None
            # Intentar varios formatos
            formatos = [
                '%d/%m/%y',
                '%d/%m/%Y',
                '%d/%m/%Y %H:%M:%S',
                '%d-%m-%Y',
                '%Y-%m-%d',
            ]
            for fmt in formatos:
                try:
                    return datetime.strptime(fecha.strip(), fmt)
                except ValueError:
                    continue
            return None
        
        datos.append({
            'cuit': cuit,
            'nombre_propietario': nombre_propietario,
            'nombre_establecimiento': nombre_establecimiento,
            'localidad': localidad,
            'departamento': departamento,
            'direccion': direccion,
            'fecha_inscripcion_operador': normalizar_fecha(fecha_inscripcion_operador),
            'tipo_carne': tipo_carne,
            'fecha_inscripcion': normalizar_fecha(fecha_inscripcion),
        })
    
    return datos


def obtener_persona_id(session: Session, cuit: str, nombre: str) -> Optional[int]:
    """Obtiene el ID de la persona por CUIT o crea una nueva."""
    # Normalizar CUIT (quitar guiones)
    cuit_normalizado = re.sub(r'[^0-9]', '', cuit) if cuit else ''
    
    # Buscar por CUIT normalizado (en la columna identificador)
    if cuit_normalizado:
        result = session.execute(
            text("SELECT id FROM personas WHERE identificador = :cuit LIMIT 1"),
            {"cuit": cuit_normalizado}
        )
        row = result.fetchone()
        if row:
            return row[0]
    
    # Crear persona nueva
    nombre_completo = nombre or "SIN NOMBRE"
    
    # Determinar tipo de documento y normalizar identificador
    if cuit_normalizado:
        # Verificar si es CUIT (11 dígitos) o DNI (8 dígitos)
        if len(cuit_normalizado) == 11:
            tipo_doc = 'CUIT'
            identificador = cuit_normalizado
        elif len(cuit_normalizado) == 8:
            tipo_doc = 'DNI'
            identificador = cuit_normalizado
        else:
            # Si el CUIT tiene una longitud inválida, usar un identificador único
            tipo_doc = 'DNI'
            # Generar un identificador único basado en el nombre y un contador
            import hashlib
            # Usar un hash del nombre + timestamp para evitar colisiones
            import time
            combined = f"{nombre_completo}-{time.time()}"
            identificador = hashlib.md5(combined.encode()).hexdigest()[:8]
    else:
        tipo_doc = 'DNI'
        identificador = '00000000'
    
    # Determinar tipo de persona (PF o PJ)
    tipo_persona = 'PJ' if any(x in nombre_completo.upper() for x in ['S.A', 'S.R.L', 'SOCIEDAD', 'ASOCIACION', 'S.A.', 'S.R.L.']) else 'PF'
    
    result = session.execute(
        text("""
            INSERT INTO personas (tipo, tipo_documento, identificador, nombre, domicilio, creado_en)
            VALUES (:tipo, :tipo_doc, :identificador, :nombre, '', NOW())
            RETURNING id
        """),
        {"tipo": tipo_persona, "tipo_doc": tipo_doc, "identificador": identificador, "nombre": nombre_completo}
    )
    session.commit()
    return result.fetchone()[0]


def obtener_operador_id(session: Session, cuit: str, nombre_establecimiento: str) -> Optional[int]:
    """Obtiene el ID del operador por CUIT o crea uno nuevo."""
    # Buscar por CUIT
    if cuit:
        result = session.execute(
            text("SELECT id FROM operadores WHERE cuit = :cuit LIMIT 1"),
            {"cuit": cuit}
        )
        row = result.fetchone()
        if row:
            return row[0]
    
    return None


def crear_operador(session: Session, persona_id: int, cuit: str, nombre: str, 
                   domicilio: str, tipo: str) -> int:
    """Crea un nuevo operador."""
    # Normalizar CUIT (quitar guiones)
    cuit_normalizado = re.sub(r'[^0-9]', '', cuit) if cuit else ''
    
    result = session.execute(
        text("""
            INSERT INTO operadores (persona_id, cuit, razon_social, domicilio_comercial, tipo, estado_registral, creado_en)
            VALUES (:persona_id, :cuit, :nombre, :domicilio, :tipo, 'ACTIVO', NOW())
            RETURNING id
        """),
        {
            "persona_id": persona_id,
            "cuit": cuit_normalizado or '',
            "nombre": nombre,
            "domicilio": domicilio,
            "tipo": tipo
        }
    )
    session.commit()
    return result.fetchone()[0]


def obtener_inscripcion_id(session: Session, operador_id: int, fecha: datetime) -> Optional[int]:
    """Obtiene el ID de la inscripción."""
    result = session.execute(
        text("""
            SELECT id FROM inscripciones 
            WHERE operador_id = :operador_id AND fecha_inscripcion = :fecha
            LIMIT 1
        """),
        {"operador_id": operador_id, "fecha": fecha}
    )
    row = result.fetchone()
    if row:
        return row[0]
    return None


def crear_inscripcion(session: Session, operador_id: int, fecha: datetime) -> int:
    """Crea una nueva inscripción."""
    # Generar número de inscripción secuencial (como texto)
    result = session.execute(text("SELECT COUNT(*) FROM inscripciones"))
    count = result.fetchone()[0]
    numero = f"INS-{count + 1:06d}"
    
    result = session.execute(
        text("""
            INSERT INTO inscripciones (operador_id, tipo, fecha_inscripcion, numero_inscripcion)
            VALUES (:operador_id, 'OPERADOR', :fecha, :numero)
            RETURNING id
        """),
        {"operador_id": operador_id, "fecha": fecha, "numero": numero}
    )
    session.commit()
    return result.fetchone()[0]


def obtener_actividad_id(session: Session, nombre: str) -> Optional[int]:
    """Obtiene el ID de la actividad económica por nombre."""
    result = session.execute(
        text("SELECT id FROM actividades_economicas WHERE descripcion = :nombre LIMIT 1"),
        {"nombre": nombre}
    )
    row = result.fetchone()
    if row:
        return row[0]
    return None


def crear_actividad(session: Session, nombre: str, grupo_id: int, subgrupo_id: Optional[int]) -> int:
    """Crea una nueva actividad económica."""
    # Generar código único
    result = session.execute(text("SELECT COUNT(*) FROM actividades_economicas"))
    count = result.fetchone()[0]
    codigo = f"ACT-{count + 1:04d}"
    
    result = session.execute(
        text("""
            INSERT INTO actividades_economicas (codigo, descripcion, alicuota, grupo_id, subgrupo_id)
            VALUES (:codigo, :nombre, 0, :grupo_id, :subgrupo_id)
            RETURNING id
        """),
        {
            "codigo": codigo,
            "nombre": nombre,
            "grupo_id": grupo_id,
            "subgrupo_id": subgrupo_id
        }
    )
    session.commit()
    return result.fetchone()[0]


def cargar_datos(ruta_archivo: str) -> None:
    """Carga los datos del archivo en la base de datos."""
    # Obtener URL de la base de datos
    db_url = os.environ.get("ROCCA_DATABASE_URL")
    if not db_url:
        print("Error: ROCCA_DATABASE_URL no está definido")
        sys.exit(1)
    
    # Crear engine
    engine = create_engine(db_url)
    
    # Parsear datos
    print(f"Parseando datos de {ruta_archivo}...")
    datos = parsear_datos(ruta_archivo)
    print(f"Se encontraron {len(datos)} registros")
    
    # Agrupar por CUIT para evitar duplicados
    # Pero mantener todos los establecimientos (sucursales)
    operadores_por_cuit = {}
    establecimientos_por_cuit = {}
    
    for dato in datos:
        cuit = dato['cuit'] or 'SIN_CUIT'
        
        # Almacenar el primer dato para cada CUIT
        if cuit not in operadores_por_cuit:
            operadores_por_cuit[cuit] = dato
        
        # Almacenar todos los establecimientos para cada CUIT
        if cuit not in establecimientos_por_cuit:
            establecimientos_por_cuit[cuit] = []
        establecimientos_por_cuit[cuit].append(dato)
    
    print(f"Se encontraron {len(operadores_por_cuit)} operadores únicos (CUITs)")
    print(f"Se encontraron {len(datos)} establecimientos en total")
    
    # Iniciar sesión
    with Session(engine) as session:
        # Obtener o crear grupo de actividades por defecto
        result = session.execute(text("SELECT id FROM grupos_actividad LIMIT 1"))
        row = result.fetchone()
        if row:
            grupo_id = row[0]
        else:
            # Crear grupo de actividades por defecto
            result = session.execute(
                text("""
                    INSERT INTO grupos_actividad (codigo, descripcion)
                    VALUES ('C', 'Actividades relacionadas con la comercialización de carne')
                    RETURNING id
                """)
            )
            session.commit()
            grupo_id = result.fetchone()[0]
            print(f"Grupo de actividades creado con ID: {grupo_id}")
        
        # Procesar cada establecimiento (sucursal)
        for cuit, establecimientos in establecimientos_por_cuit.items():
            dato = establecimientos[0]  # Usar el primer establecimiento para los datos del operador
            
            print(f"\nProcesando CUIT: {cuit} ({len(establecimientos)} establecimientos)")
            
            # 1. Obtener o crear persona (una por CUIT)
            persona_id = obtener_persona_id(session, cuit, dato['nombre_propietario'])
            print(f"  Persona ID: {persona_id}")
            
            # 2. Procesar cada establecimiento
            for estab in establecimientos:
                nombre_establecimiento = estab['nombre_establecimiento'] or estab['nombre_propietario'] or 'SIN NOMBRE'
                domicilio = estab['direccion'] or ''
                tipo = 'ESTABLECIMIENTO'
                
                print(f"    Establecimiento: {nombre_establecimiento}")
                
                # Obtener o crear operador (uno por establecimiento)
                # Primero buscar por persona_id (ya que cada persona solo puede tener un operador)
                result = session.execute(
                    text("SELECT id FROM operadores WHERE persona_id = :persona_id LIMIT 1"),
                    {"persona_id": persona_id}
                )
                row = result.fetchone()
                if row:
                    operador_id = row[0]
                    print(f"      Operador existente (por persona) con ID: {operador_id}")
                else:
                    # Buscar por CUIT (ya que cada CUIT solo puede tener un operador)
                    cuit_normalizado = re.sub(r'[^0-9]', '', cuit) if cuit else ''
                    result = session.execute(
                        text("SELECT id FROM operadores WHERE cuit = :cuit LIMIT 1"),
                        {"cuit": cuit_normalizado}
                    )
                    row = result.fetchone()
                    if row:
                        operador_id = row[0]
                        print(f"      Operador existente (por CUIT) con ID: {operador_id}")
                    else:
                        # Crear nuevo operador
                        operador_id = crear_operador(session, persona_id, cuit, nombre_establecimiento, domicilio, tipo)
                        print(f"      Operador creado con ID: {operador_id}")
                
                # Obtener o crear inscripción
                fecha_inscripcion = estab['fecha_inscripcion'] or datetime.now()
                inscripcion_id = obtener_inscripcion_id(session, operador_id, fecha_inscripcion)
                if not inscripcion_id:
                    inscripcion_id = crear_inscripcion(session, operador_id, fecha_inscripcion)
                    print(f"      Inscripción creada con ID: {inscripcion_id}")
                else:
                    print(f"      Inscripción existente con ID: {inscripcion_id}")
                
                # Obtener o crear actividad económica
                tipo_carne = estab['tipo_carne'] or 'BOVINO'
                actividad_id = obtener_actividad_id(session, tipo_carne)
                if not actividad_id:
                    actividad_id = crear_actividad(session, tipo_carne, grupo_id, None)
                    print(f"      Actividad económica creada con ID: {actividad_id}")
                else:
                    print(f"      Actividad económica existente con ID: {actividad_id}")
                
                # Crear requisito de inscripción (vincular operador-inscripción-actividad)
                # La tabla requisitos_inscripcion tiene una estructura diferente
                # Por ahora, solo creamos el requisito básico
                result = session.execute(
                    text("""
                        SELECT id FROM requisitos_inscripcion 
                        WHERE operador_id = :operador_id AND codigo = :codigo
                        LIMIT 1
                    """),
                    {"operador_id": operador_id, "codigo": 'ACTIVO'}
                )
                row = result.fetchone()
                if not row:
                    session.execute(
                        text("""
                            INSERT INTO requisitos_inscripcion (operador_id, codigo, descripcion, es_general, cumplido, fecha_cumplimiento, creado_en)
                            VALUES (:operador_id, 'ACTIVO', 'Inscripción como operador', false, true, NOW(), NOW())
                        """),
                        {"operador_id": operador_id}
                    )
                    session.commit()
                    print(f"      Requisito de inscripción creado")
                else:
                    print(f"      Requisito de inscripción ya existe")
    
    print("\n¡Carga completada!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/cargar_operadores.py <archivo_de_datos>")
        sys.exit(1)
    
    ruta_archivo = sys.argv[1]
    if not Path(ruta_archivo).exists():
        print(f"Error: El archivo {ruta_archivo} no existe")
        sys.exit(1)
    
    cargar_datos(ruta_archivo)
