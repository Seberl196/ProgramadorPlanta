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
    tipo = (
        "asignacion"
        if tren_origen_id is None
        else "movimiento"
    )

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