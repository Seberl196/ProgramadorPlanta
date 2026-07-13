from datetime import datetime

from database.connection import get_connection


def create_tables() -> None:
    """
    Crea las tablas necesarias para el aplicativo.

    La instrucción IF NOT EXISTS permite ejecutar esta función varias
    veces sin borrar ni modificar los datos existentes.
    """
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS trenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT,
                activo INTEGER NOT NULL DEFAULT 1
                    CHECK (activo IN (0, 1)),
                fecha_creacion TEXT NOT NULL,
                fecha_modificacion TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS configuracion_trenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tren_id INTEGER NOT NULL UNIQUE,
                inicio_programacion TEXT NOT NULL,
                eficiencia_predeterminada REAL NOT NULL DEFAULT 0.50
                    CHECK (
                        eficiencia_predeterminada > 0
                        AND eficiencia_predeterminada <= 1
                    ),
                fecha_modificacion TEXT NOT NULL,

                FOREIGN KEY (tren_id)
                    REFERENCES trenes(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS ordenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tren_id INTEGER NOT NULL,
                posicion INTEGER NOT NULL,

                numero_ot TEXT NOT NULL UNIQUE,
                referencia TEXT NOT NULL,
                cliente TEXT,
                descripcion TEXT,

                cantidad REAL NOT NULL
                    CHECK (cantidad > 0),

                fecha_entrega TEXT,

                produccion_hora_teorica REAL NOT NULL
                    CHECK (produccion_hora_teorica > 0),

                eficiencia REAL NOT NULL
                    CHECK (
                        eficiencia > 0
                        AND eficiencia <= 1
                    ),

                produccion_hora_estimada REAL,
                tiempo_produccion REAL,

                tiempo_alistamiento REAL NOT NULL DEFAULT 0
                    CHECK (tiempo_alistamiento >= 0),

                tiempo_adicional REAL NOT NULL DEFAULT 0
                    CHECK (tiempo_adicional >= 0),

                tiempo_total REAL,

                fecha_inicio TEXT,
                fecha_final TEXT,

                tela_enrollada TEXT NOT NULL DEFAULT 'No'
                    CHECK (tela_enrollada IN ('Sí', 'No')),

                tela_cortada TEXT NOT NULL DEFAULT 'No'
                    CHECK (tela_cortada IN ('Sí', 'No')),

                piezas_metalicas TEXT NOT NULL DEFAULT 'No'
                    CHECK (
                        piezas_metalicas IN (
                            'Sí',
                            'No',
                            'Pendiente de aprobación'
                        )
                    ),

                otros_materiales TEXT NOT NULL DEFAULT 'No'
                    CHECK (
                        otros_materiales IN (
                            'Sí',
                            'No',
                            'Pendiente de aprobación'
                        )
                    ),

                observaciones TEXT,

                fecha_creacion TEXT NOT NULL,
                fecha_modificacion TEXT NOT NULL,

                FOREIGN KEY (tren_id)
                    REFERENCES trenes(id)
                    ON DELETE CASCADE,

                UNIQUE (tren_id, posicion)
            );

            CREATE INDEX IF NOT EXISTS idx_ordenes_tren_posicion
            ON ordenes (tren_id, posicion);

            CREATE INDEX IF NOT EXISTS idx_ordenes_fecha_entrega
            ON ordenes (fecha_entrega);
            """
        )


def insert_initial_data() -> None:
    """
    Inserta el Tren 1 y su configuración inicial.

    Los datos se insertan únicamente si todavía no existen.
    """
    now = datetime.now().replace(microsecond=0)
    now_iso = now.isoformat()

    # En la primera creación se utiliza hoy a las 06:00.
    default_start = now.replace(
        hour=6,
        minute=0,
        second=0,
        microsecond=0,
    ).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO trenes (
                id,
                nombre,
                descripcion,
                activo,
                fecha_creacion,
                fecha_modificacion
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                "Tren 1",
                "Primera línea de producción del prototipo",
                1,
                now_iso,
                now_iso,
            ),
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO configuracion_trenes (
                tren_id,
                inicio_programacion,
                eficiencia_predeterminada,
                fecha_modificacion
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                1,
                default_start,
                0.50,
                now_iso,
            ),
        )


def initialize_database() -> None:
    """
    Inicializa completamente la base de datos.

    Puede ejecutarse cada vez que arranque la aplicación sin eliminar
    ni sobrescribir la información existente.
    """
    create_tables()
    insert_initial_data()