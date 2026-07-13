import sqlite3

from data.conexion import obtener_conexion


def _obtener_columnas(
    conexion: sqlite3.Connection,
    nombre_tabla: str,
) -> set[str]:
    """
    Devuelve los nombres de las columnas de una tabla.
    """
    filas = conexion.execute(f"PRAGMA table_info({nombre_tabla})").fetchall()

    return {fila["name"] for fila in filas}


def crear_tabla_ordenes() -> None:
    """
    Crea la tabla de órdenes y añade columnas nuevas
    sin eliminar los datos existentes.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS ordenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                posicion INTEGER NOT NULL,
                numero_ot TEXT NOT NULL UNIQUE,
                duracion_horas REAL NOT NULL,
                estado TEXT NOT NULL DEFAULT 'pendiente',
                fecha_inicio_real TEXT,
                fecha_fin_real TEXT,
                horas_producidas REAL NOT NULL DEFAULT 0,
                inicio_manual TEXT
            )
            """
        )

        columnas = _obtener_columnas(
            conexion,
            "ordenes",
        )

        columnas_nuevas = {
            "estado": ("TEXT NOT NULL DEFAULT 'pendiente'"),
            "fecha_inicio_real": "TEXT",
            "fecha_fin_real": "TEXT",
            "horas_producidas": ("REAL NOT NULL DEFAULT 0"),
            "inicio_manual": "TEXT",
        }

        for nombre, definicion in columnas_nuevas.items():
            if nombre not in columnas:
                conexion.execute(
                    f"""
                    ALTER TABLE ordenes
                    ADD COLUMN {nombre} {definicion}
                    """
                )


def crear_tabla_estado_tren() -> None:
    """
    Crea la tabla que guarda el estado persistente
    del Tren 1.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS estado_tren (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                proximo_inicio TEXT,
                programacion_activa INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        conexion.execute(
            """
            INSERT OR IGNORE INTO estado_tren (
                id,
                proximo_inicio,
                programacion_activa
            )
            VALUES (1, NULL, 0)
            """
        )


def inicializar_base_de_datos() -> None:
    """
    Ejecuta todas las migraciones necesarias.
    """
    crear_tabla_ordenes()
    crear_tabla_estado_tren()
