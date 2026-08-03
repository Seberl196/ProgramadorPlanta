from datetime import datetime
from data.programacion_ordenes import reorganizar_posiciones
from data.conexion import obtener_conexion
from data.consultas_ordenes import obtener_tren_id_de_orden

def agregar_orden(
    numero_ot: str,
    duracion_horas: float,
    tren_id: int,
) -> None:
    """
    Añade una OT al final de la cola activa
    del tren indicado.
    """
    with obtener_conexion() as conexion:
        resultado = conexion.execute(
            """
            SELECT
                COALESCE(MAX(posicion), 0) + 1
                AS siguiente_posicion
            FROM ordenes
            WHERE estado IN (
                'pendiente',
                'en_produccion'
            )

                          AND tren_id = ?
            """,
            (tren_id,),
        ).fetchone()

        conexion.execute(
            """
            INSERT INTO ordenes (
                posicion,
                numero_ot,
                duracion_horas,
                estado,
                horas_producidas,
                tren_id
            )
            VALUES (?, ?, ?, 'pendiente', 0, ?)
            """,
            (
                int(resultado["siguiente_posicion"]),
                numero_ot.strip(),
                float(duracion_horas),
                tren_id,
            ),
        )


def actualizar_orden(
    orden_id: int,
    numero_ot: str,
    duracion_horas: float,
    inicio_manual: datetime | None = None,
) -> None:
    """
    Actualiza los datos editables de una OT.
    """
    inicio_manual_texto = (
        inicio_manual.isoformat() if inicio_manual is not None else None
    )

    with obtener_conexion() as conexion:
        conexion.execute(
            """
            UPDATE ordenes
            SET
                numero_ot = ?,
                duracion_horas = ?,
                inicio_manual = ?
            WHERE id = ?
              AND estado != 'terminada'
            """,
            (
                numero_ot.strip(),
                float(duracion_horas),
                inicio_manual_texto,
                orden_id,
            ),
        )


def eliminar_orden(
    orden_id: int,
    tren_id: int,
) -> None:
    """
    Elimina una OT pendiente.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            DELETE FROM ordenes
            WHERE id = ?
              AND  tren_id = ?
              AND estado = 'pendiente'
            """,
            (orden_id, tren_id),
        )

    reorganizar_posiciones(tren_id)
