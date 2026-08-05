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


def _existe_tabla(
    conexion: sqlite3.Connection,
    nombre_tabla: str,
) -> bool:
    """
    Comprueba si una tabla existe en SQLite.
    """
    fila = conexion.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (nombre_tabla,),
    ).fetchone()

    return fila is not None


def crear_tabla_trenes() -> None:
    """
    Crea el catálogo de trenes.

    Cada tren registra sus posiciones de ojos y sus
    capacidades de costura. Los horarios laborales
    se configurarán posteriormente en tablas separadas.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS trenes (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT,
                activo INTEGER NOT NULL DEFAULT 1,
                orden_visual INTEGER NOT NULL,
                posiciones_ojos INTEGER NOT NULL DEFAULT 0,
                costura_visible INTEGER NOT NULL DEFAULT 0,
                costura_invisible INTEGER NOT NULL DEFAULT 0,
                costura_reforzada INTEGER NOT NULL DEFAULT 0,

                CHECK (activo IN (0, 1)),
                CHECK (posiciones_ojos >= 0),
                CHECK (costura_visible IN (0, 1)),
                CHECK (costura_invisible IN (0, 1)),
                CHECK (costura_reforzada IN (0, 1))
            )
            """
        )

        trenes_iniciales = [
            (
                1,
                "Tren 1",
                None,
                1,
                1,
                0,
                0,
                0,
                0,
            ),
            (
                2,
                "Tren 2",
                None,
                1,
                2,
                0,
                0,
                0,
                0,
            ),
            (
                3,
                "Tren 3",
                None,
                1,
                3,
                0,
                0,
                0,
                0,
            ),
        ]

        conexion.executemany(
            """
            INSERT OR IGNORE INTO trenes (
                id,
                nombre,
                descripcion,
                activo,
                orden_visual,
                posiciones_ojos,
                costura_visible,
                costura_invisible,
                costura_reforzada
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trenes_iniciales,
        )


def crear_tabla_maquinas() -> None:
    """
    Crea el catálogo de máquinas asociadas a los trenes.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS maquinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tren_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                posicion INTEGER NOT NULL,
                serial TEXT NOT NULL UNIQUE,
                activo INTEGER NOT NULL DEFAULT 1,

                FOREIGN KEY (tren_id)
                    REFERENCES trenes(id),

                UNIQUE (tren_id, tipo, posicion),

                CHECK (tipo IN ('ojos', 'ganchos')),
                CHECK (posicion >= 1),
                CHECK (activo IN (0, 1))
            )
            """
        )

        conexion.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_maquinas_tren_id
            ON maquinas (tren_id)
            """
        )


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
                posicion INTEGER,
                numero_ot TEXT NOT NULL,
                duracion_horas REAL NOT NULL,
                estado TEXT NOT NULL DEFAULT 'entrada',
                horas_producidas REAL NOT NULL DEFAULT 0,
                fecha_inicio_real TEXT,
                fecha_fin_real TEXT,
                inicio_manual TEXT,
                tren_id INTEGER,

                FOREIGN KEY (tren_id)
                    REFERENCES trenes(id),

                CHECK (
                    estado IN (
                        'entrada',
                        'pendiente',
                        'en_produccion',
                        'pausada',
                        'terminada'
                    )
                )
            )
            """
        )

        columnas = _obtener_columnas(
            conexion,
            "ordenes",
        )

        columnas_nuevas = {
            "estado": "TEXT NOT NULL DEFAULT 'pendiente'",
            "fecha_inicio_real": "TEXT",
            "fecha_fin_real": "TEXT",
            "horas_producidas": "REAL NOT NULL DEFAULT 0",
            "inicio_manual": "TEXT",
            "tren_id": "INTEGER NOT NULL DEFAULT 1",
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
    Crea un estado de programación independiente
    para cada tren.

    Migra automáticamente la estructura antigua
    que utilizaba la columna id.
    """
    with obtener_conexion() as conexion:
        if _existe_tabla(conexion, "estado_tren"):
            columnas = _obtener_columnas(
                conexion,
                "estado_tren",
            )

            if "tren_id" not in columnas:
                if _existe_tabla(
                    conexion,
                    "estado_tren_antiguo",
                ):
                    conexion.execute(
                        """
                        DROP TABLE estado_tren_antiguo
                        """
                    )

                conexion.execute(
                    """
                    ALTER TABLE estado_tren
                    RENAME TO estado_tren_antiguo
                    """
                )

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS estado_tren (
                tren_id INTEGER PRIMARY KEY,
                proximo_inicio TEXT,
                programacion_activa INTEGER NOT NULL DEFAULT 0,

                FOREIGN KEY (tren_id)
                    REFERENCES trenes(id),

                CHECK (programacion_activa IN (0, 1))
            )
            """
        )

        if _existe_tabla(
            conexion,
            "estado_tren_antiguo",
        ):
            columnas_antiguas = _obtener_columnas(
                conexion,
                "estado_tren_antiguo",
            )

            if "id" in columnas_antiguas:
                conexion.execute(
                    """
                    INSERT OR IGNORE INTO estado_tren (
                        tren_id,
                        proximo_inicio,
                        programacion_activa
                    )
                    SELECT
                        id,
                        proximo_inicio,
                        programacion_activa
                    FROM estado_tren_antiguo
                    """
                )

            conexion.execute(
                """
                DROP TABLE estado_tren_antiguo
                """
            )

        trenes = conexion.execute(
            """
            SELECT id
            FROM trenes
            ORDER BY orden_visual ASC
            """
        ).fetchall()

        conexion.executemany(
            """
            INSERT OR IGNORE INTO estado_tren (
                tren_id,
                proximo_inicio,
                programacion_activa
            )
            VALUES (?, NULL, 0)
            """,
            [(tren["id"],) for tren in trenes],
        )


def crear_tabla_historial_produccion() -> None:
    """
    Crea el historial de eventos de producción de las OT.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS historial_produccion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_id INTEGER NOT NULL,
                tren_id INTEGER NOT NULL,
                evento TEXT NOT NULL,
                fecha_hora TEXT NOT NULL,
                horas_producidas REAL,

                FOREIGN KEY (orden_id)
                    REFERENCES ordenes(id),

                FOREIGN KEY (tren_id)
                    REFERENCES trenes(id),

                CHECK (
                    evento IN (
                        'iniciada',
                        'pausada',
                        'reanudada',
                        'terminada'
                    )
                )
            )
            """
        )

        conexion.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_historial_produccion_orden_id
            ON historial_produccion (orden_id)
            """
        )

        conexion.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_historial_produccion_tren_id
            ON historial_produccion (tren_id)
            """
        )


def crear_tabla_historial_movimientos() -> None:
    """
    Crea el historial de asignaciones y movimientos de las OT.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS historial_movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_id INTEGER NOT NULL,
                tren_origen_id INTEGER,
                tren_destino_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                fecha_hora TEXT NOT NULL,

                FOREIGN KEY (orden_id)
                    REFERENCES ordenes(id),

                FOREIGN KEY (tren_origen_id)
                    REFERENCES trenes(id),

                FOREIGN KEY (tren_destino_id)
                    REFERENCES trenes(id),

                CHECK (
                    tipo IN (
                        'asignacion',
                        'movimiento'
                    )
                )
            )
            """
        )


def inicializar_base_de_datos() -> None:
    """
    Ejecuta todas las migraciones necesarias.
    """
    crear_tabla_trenes()
    crear_tabla_maquinas()
    crear_tabla_ordenes()
    crear_tabla_estado_tren()
    crear_tabla_historial_produccion()
    crear_tabla_historial_movimientos()
