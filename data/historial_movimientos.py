from datetime import datetime

from data.conexion import obtener_conexion


def registrar_movimiento_orden(
    orden_id: int,
    tren_destino_id: int,
    tren_origen_id: int | None = None,
) -> None:
    """
    Registra una asignación inicial o un movimiento entre trenes.
    """
    tipo = "asignacion" if tren_origen_id is None else "movimiento"

    with obtener_conexion() as conexion:
        conexion.execute(
            """
            INSERT INTO historial_movimientos (
                orden_id,
                tren_origen_id,
                tren_destino_id,
                tipo,
                fecha_hora
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                orden_id,
                tren_origen_id,
                tren_destino_id,
                tipo,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )


def obtener_movimientos_orden(
    orden_id: int,
) -> list[dict]:
    """
    Obtiene las asignaciones y movimientos registrados para una OT.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT
                hm.id,
                hm.tipo,
                hm.fecha_hora,
                hm.tren_origen_id,
                origen.nombre AS nombre_tren_origen,
                hm.tren_destino_id,
                destino.nombre AS nombre_tren_destino
            FROM historial_movimientos AS hm
            LEFT JOIN trenes AS origen
                ON origen.id = hm.tren_origen_id
            INNER JOIN trenes AS destino
                ON destino.id = hm.tren_destino_id
            WHERE hm.orden_id = ?
            ORDER BY hm.fecha_hora ASC, hm.id ASC
            """,
            (orden_id,),
        ).fetchall()

    return [dict(fila) for fila in filas]
