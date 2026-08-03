from datetime import datetime

from data.conexion import obtener_conexion


def registrar_evento_produccion(
    orden_id: int,
    tren_id: int,
    evento: str,
    horas_producidas: float | None = None,
    fecha_hora: datetime | None = None,
) -> None:
    """
    Registra un evento en el historial de producción.
    """
    if fecha_hora is None:
        fecha_hora = datetime.now()

    with obtener_conexion() as conexion:
        conexion.execute(
            """
            INSERT INTO historial_produccion (
                orden_id,
                tren_id,
                evento,
                fecha_hora,
                horas_producidas
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                orden_id,
                tren_id,
                evento,
                fecha_hora.isoformat(timespec="seconds"),
                horas_producidas,
            ),
        )

def obtener_historial_produccion(
    tren_id: int,
) -> list[dict]:
    """
    Obtiene el historial de eventos de producción de un tren.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT
                hp.id,
                hp.orden_id,
                o.numero_ot,
                hp.tren_id,
                t.nombre AS nombre_tren,
                hp.evento,
                hp.fecha_hora,
                hp.horas_producidas
            FROM historial_produccion AS hp
            INNER JOIN ordenes AS o
                ON o.id = hp.orden_id
            INNER JOIN trenes AS t
                ON t.id = hp.tren_id
            WHERE hp.tren_id = ?
            ORDER BY hp.fecha_hora DESC, hp.id DESC
            """,
            (tren_id,),
        ).fetchall()

    return [dict(fila) for fila in filas]