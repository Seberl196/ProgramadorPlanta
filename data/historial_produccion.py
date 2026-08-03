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