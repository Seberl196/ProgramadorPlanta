from datetime import datetime

from data.conexion import obtener_conexion


def obtener_estado_tren() -> dict:
    """
    Devuelve el estado persistente del Tren 1.
    """
    with obtener_conexion() as conexion:
        fila = conexion.execute(
            """
            SELECT
                proximo_inicio,
                programacion_activa
            FROM estado_tren
            WHERE id = 1
            """
        ).fetchone()

    if fila is None:
        return {
            "proximo_inicio": None,
            "programacion_activa": False,
        }

    return {
        "proximo_inicio": fila["proximo_inicio"],
        "programacion_activa": bool(fila["programacion_activa"]),
    }


def definir_inicio_programacion(
    proximo_inicio: datetime,
) -> None:
    """
    Inicia una nueva secuencia de programación.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            UPDATE estado_tren
            SET
                proximo_inicio = ?,
                programacion_activa = 1
            WHERE id = 1
            """,
            (proximo_inicio.isoformat(),),
        )


def actualizar_proximo_inicio(
    proximo_inicio: datetime,
) -> None:
    """
    Actualiza el próximo momento disponible del tren.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            UPDATE estado_tren
            SET
                proximo_inicio = ?,
                programacion_activa = 1
            WHERE id = 1
            """,
            (proximo_inicio.isoformat(),),
        )


def cerrar_programacion() -> None:
    """
    Cierra la secuencia actual.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            UPDATE estado_tren
            SET
                proximo_inicio = NULL,
                programacion_activa = 0
            WHERE id = 1
            """
        )
