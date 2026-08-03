from datetime import datetime

from data.conexion import obtener_conexion


def obtener_estado_tren(
    tren_id: int,
) -> dict:
    """
    Devuelve el estado persistente del tren indicado.
    """
    with obtener_conexion() as conexion:
        fila = conexion.execute(
            """
            SELECT
                proximo_inicio,
                programacion_activa
            FROM estado_tren
            WHERE tren_id = ?
            """,
            (tren_id,),
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
    tren_id: int,
) -> None:
    """
    Inicia una nueva secuencia de programación
    para el tren indicado.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            UPDATE estado_tren
            SET
                proximo_inicio = ?,
                programacion_activa = 1
            WHERE tren_id = ?
            """,
            (
                proximo_inicio.isoformat(),
                tren_id,
            ),
        )


def actualizar_proximo_inicio(
    proximo_inicio: datetime,
    tren_id: int,
) -> None:
    """
    Actualiza el próximo momento disponible
    del tren indicado.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            UPDATE estado_tren
            SET
                proximo_inicio = ?,
                programacion_activa = 1
            WHERE tren_id = ?
            """,
            (
                proximo_inicio.isoformat(),
                tren_id,
            ),
        )


def cerrar_programacion(
    tren_id: int,
) -> None:
    """
    Cierra la secuencia actual del tren indicado.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            UPDATE estado_tren
            SET
                proximo_inicio = NULL,
                programacion_activa = 0
            WHERE tren_id = ?
            """,
            (tren_id,),
        )
