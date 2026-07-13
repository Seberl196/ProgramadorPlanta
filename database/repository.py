from datetime import datetime
from typing import Any

from database.connection import get_connection


def get_train(train_id: int) -> dict[str, Any] | None:
    """
    Obtiene un tren por su identificador.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                nombre,
                descripcion,
                activo,
                fecha_creacion,
                fecha_modificacion
            FROM trenes
            WHERE id = ?
            """,
            (train_id,),
        ).fetchone()

    return dict(row) if row else None


def get_train_configuration(train_id: int) -> dict[str, Any] | None:
    """
    Obtiene la configuración correspondiente a un tren.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                tren_id,
                inicio_programacion,
                eficiencia_predeterminada,
                fecha_modificacion
            FROM configuracion_trenes
            WHERE tren_id = ?
            """,
            (train_id,),
        ).fetchone()

    return dict(row) if row else None


def update_train_start(
    train_id: int,
    start_datetime: datetime,
) -> None:
    """
    Actualiza la fecha y hora de inicio de programación de un tren.
    """
    start_iso = start_datetime.replace(microsecond=0).isoformat()
    modification_iso = datetime.now().replace(microsecond=0).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE configuracion_trenes
            SET
                inicio_programacion = ?,
                fecha_modificacion = ?
            WHERE tren_id = ?
            """,
            (
                start_iso,
                modification_iso,
                train_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"No existe una configuración para el tren con ID {train_id}."
            )