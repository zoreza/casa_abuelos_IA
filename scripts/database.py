"""
Gestión de base de datos SQLite para persistencia de conversaciones
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from config import DATABASE_PATH

# ============================================
# INICIALIZACIÓN DE BASE DE DATOS
# ============================================

def inicializar_db():
    """Crea tablas de base de datos si no existen"""
    DB_PATH = Path(DATABASE_PATH)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Tabla de conversaciones
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            pregunta TEXT NOT NULL,
            respuesta TEXT NOT NULL,
            modelo_usado TEXT DEFAULT 'desconocido',
            tiempo_respuesta_segundos REAL DEFAULT 0,
            exitosa INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de leads/prospectos
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT UNIQUE NOT NULL,
            nombre TEXT,
            email TEXT,
            telefono TEXT,
            fecha_primer_contacto TEXT NOT NULL,
            fecha_ultima_consulta TEXT NOT NULL,
            estado TEXT DEFAULT 'prospecto',
            notas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de reservas exitosas
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            num_personas INTEGER NOT NULL,
            costo_total REAL NOT NULL,
            apartado REAL NOT NULL,
            estado TEXT DEFAULT 'confirmada',
            notas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de métricas
    c.execute('''
        CREATE TABLE IF NOT EXISTS metricas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            total_consultas INTEGER DEFAULT 0,
            consultas_correctas INTEGER DEFAULT 0,
            consultas_error INTEGER DEFAULT 0,
            tiempo_promedio_respuesta REAL DEFAULT 0,
            tasa_exito REAL DEFAULT 0,
            modelo_mas_usado TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear índices para búsquedas rápidas
    c.execute('CREATE INDEX IF NOT EXISTS idx_cliente_id ON conversaciones(cliente_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON conversaciones(timestamp)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_leads_cliente ON leads(cliente_id)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Base de datos inicializada: {DATABASE_PATH}")


# ============================================
# OPERACIONES DE CONVERSACIONES
# ============================================

def guardar_conversacion(
    cliente_id: str,
    pregunta: str,
    respuesta: str,
    modelo_usado: str = "desconocido",
    tiempo_respuesta_segundos: float = 0,
    exitosa: bool = True
) -> int:
    """
    Guarda una conversación en la base de datos
    
    Returns:
        ID de la conversación guardada
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO conversaciones 
        (cliente_id, timestamp, pregunta, respuesta, modelo_usado, tiempo_respuesta_segundos, exitosa)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (cliente_id, timestamp, pregunta, respuesta, modelo_usado, tiempo_respuesta_segundos, 1 if exitosa else 0))
    
    conn.commit()
    conversation_id = c.lastrowid
    conn.close()
    
    return conversation_id


def obtener_historial(cliente_id: str, limit: int = 10) -> List[Dict]:
    """
    Obtiene el historial de conversaciones de un cliente
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT id, cliente_id, timestamp, pregunta, respuesta, modelo_usado, tiempo_respuesta_segundos
        FROM conversaciones
        WHERE cliente_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (cliente_id, limit))
    
    resultados = [dict(row) for row in c.fetchall()]
    conn.close()
    
    # Invertir orden para que sea cronológico (más antiguo primero)
    return resultados[::-1]


def obtener_estadisticas_cliente(cliente_id: str) -> Dict:
    """
    Obtiene estadísticas de interacción con un cliente
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            COUNT(*) as total_consultas,
            SUM(CASE WHEN exitosa = 1 THEN 1 ELSE 0 END) as consultas_exitosas,
            AVG(tiempo_respuesta_segundos) as tiempo_promedio,
            MAX(timestamp) as ultima_consulta
        FROM conversaciones
        WHERE cliente_id = ?
    ''', (cliente_id,))
    
    resultado = c.fetchone()
    conn.close()
    
    if resultado:
        return {
            "total_consultas": resultado[0] or 0,
            "consultas_exitosas": resultado[1] or 0,
            "tiempo_promedio": round(resultado[2] or 0, 2),
            "ultima_consulta": resultado[3]
        }
    
    return {"total_consultas": 0, "consultas_exitosas": 0, "tiempo_promedio": 0}


# ============================================
# OPERACIONES DE LEADS
# ============================================

def crear_o_actualizar_lead(
    cliente_id: str,
    nombre: Optional[str] = None,
    email: Optional[str] = None,
    telefono: Optional[str] = None,
    estado: str = "prospecto"
) -> int:
    """
    Crea o actualiza un lead en la base de datos
    
    Returns:
        ID del lead
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Verificar si el lead ya existe
    c.execute('SELECT id FROM leads WHERE cliente_id = ?', (cliente_id,))
    existente = c.fetchone()
    
    if existente:
        # Actualizar
        c.execute('''
            UPDATE leads
            SET nombre = COALESCE(?, nombre),
                email = COALESCE(?, email),
                telefono = COALESCE(?, telefono),
                estado = ?,
                fecha_ultima_consulta = ?,
                updated_at = ?
            WHERE cliente_id = ?
        ''', (nombre, email, telefono, estado, timestamp, timestamp, cliente_id))
        lead_id = existente[0]
    else:
        # Crear nuevo
        c.execute('''
            INSERT INTO leads
            (cliente_id, nombre, email, telefono, estado, fecha_primer_contacto, fecha_ultima_consulta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cliente_id, nombre, email, telefono, estado, timestamp, timestamp))
        lead_id = c.lastrowid
    
    conn.commit()
    conn.close()
    
    return lead_id


def obtener_leads(estado: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    Obtiene leads, opcionalmente filtrados por estado
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if estado:
        c.execute('''
            SELECT id, cliente_id, nombre, email, telefono, estado, fecha_primer_contacto, fecha_ultima_consulta
            FROM leads
            WHERE estado = ?
            ORDER BY fecha_ultima_consulta DESC
            LIMIT ?
        ''', (estado, limit))
    else:
        c.execute('''
            SELECT id, cliente_id, nombre, email, telefono, estado, fecha_primer_contacto, fecha_ultima_consulta
            FROM leads
            ORDER BY fecha_ultima_consulta DESC
            LIMIT ?
        ''', (limit,))
    
    resultados = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return resultados


# ============================================
# OPERACIONES DE RESERVAS
# ============================================

def guardar_reserva(
    cliente_id: str,
    fecha_inicio: str,
    fecha_fin: str,
    num_personas: int,
    costo_total: float,
    apartado: float,
    notas: str = ""
) -> int:
    """
    Guarda una reserva exitosa
    
    Returns:
        ID de la reserva
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO reservas
        (cliente_id, fecha_inicio, fecha_fin, num_personas, costo_total, apartado, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (cliente_id, fecha_inicio, fecha_fin, num_personas, costo_total, apartado, notas))
    
    conn.commit()
    reserva_id = c.lastrowid
    conn.close()
    
    # Actualizar lead a estado "cliente"
    crear_o_actualizar_lead(cliente_id, estado="cliente")
    
    return reserva_id


def obtener_reservas(cliente_id: Optional[str] = None) -> List[Dict]:
    """
    Obtiene reservas, opcionalmente de un cliente específico
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if cliente_id:
        c.execute('''
            SELECT id, cliente_id, fecha_inicio, fecha_fin, num_personas, costo_total, apartado, estado
            FROM reservas
            WHERE cliente_id = ?
            ORDER BY fecha_inicio DESC
        ''', (cliente_id,))
    else:
        c.execute('''
            SELECT id, cliente_id, fecha_inicio, fecha_fin, num_personas, costo_total, apartado, estado
            FROM reservas
            ORDER BY fecha_inicio DESC
        ''')
    
    resultados = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return resultados


# ============================================
# OPERACIONES DE MÉTRICAS
# ============================================

def guardar_metricas(metricas_dict: Dict) -> int:
    """
    Guarda un resumen de métricas del día
    """
    fecha = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO metricas
        (fecha, total_consultas, consultas_correctas, consultas_error, tiempo_promedio_respuesta, tasa_exito, modelo_mas_usado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        fecha,
        metricas_dict.get('total_consultas', 0),
        metricas_dict.get('consultas_correctas', 0),
        metricas_dict.get('consultas_error', 0),
        metricas_dict.get('tiempo_promedio_respuesta', 0),
        metricas_dict.get('tasa_exito_porcentaje', 0),
        metricas_dict.get('modelo_mas_usado', 'desconocido')
    ))
    
    conn.commit()
    metricas_id = c.lastrowid
    conn.close()
    
    return metricas_id


def obtener_metricas_periodo(dias: int = 7) -> List[Dict]:
    """
    Obtiene métricas de los últimos N días
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT fecha, total_consultas, consultas_correctas, consultas_error, 
               tiempo_promedio_respuesta, tasa_exito
        FROM metricas
        WHERE fecha >= date('now', '-' || ? || ' days')
        ORDER BY fecha DESC
    ''', (dias,))
    
    resultados = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return resultados


# Inicializar DB al importar este módulo
inicializar_db()
