from datetime import datetime

from data.conexion import obtener_conexion
from data.consultas_ordenes import obtener_tren_id_de_orden
from data.historial_movimientos import registrar_movimiento_orden
from data.programacion_ordenes import reorganizar_posiciones


def agregar_orden(
    numero_ot: str,
    duracion_horas: float,
) -> None:
    """
    Añade una OT a la bandeja de entrada.
    """
    with obtener_conexion() as conexion:
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
            VALUES (
                NULL,
                ?,
                ?,
                'entrada',
                0,
                NULL
            )
            """,
            (
                numero_ot.strip(),
                float(duracion_horas),
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
) -> None:
    """
    Elimina una OT pendiente.
    """
    tren_id = obtener_tren_id_de_orden(orden_id)

    with obtener_conexion() as conexion:
        conexion.execute(
            """
            DELETE FROM ordenes
            WHERE id = ?
              AND estado = 'pendiente'
            """,
            (orden_id,),
        )

    reorganizar_posiciones(tren_id)


def asignar_orden_a_tren(
    orden_id: int,
    tren_id: int,
) -> None:
    """
    Asigna una OT de la bandeja de entrada a un tren.
    """
    with obtener_conexion() as conexion:
        ultima_posicion = conexion.execute(
            """
            SELECT COALESCE(MAX(posicion), 0)
            FROM ordenes
            WHERE tren_id = ?
              AND estado != 'terminada'
            """,
            (tren_id,),
        ).fetchone()[0]

        conexion.execute(
            """
            UPDATE ordenes
            SET
                tren_id = ?,
                posicion = ?,
                estado = 'pendiente'
            WHERE id = ?
              AND estado = 'entrada'
            """,
            (
                tren_id,
                ultima_posicion + 1,
                orden_id,
            ),
        )
    registrar_movimiento_orden(
        orden_id=orden_id,
        tren_destino_id=tren_id,
    )


def mover_orden_a_tren(
    orden_id: int,
    tren_destino_id: int,
) -> None:
    """
    Mueve una OT pendiente o pausada a otro tren.
    """
    with obtener_conexion() as conexion:
        orden = conexion.execute(
            """
            SELECT
                tren_id,
                estado
            FROM ordenes
            WHERE id = ?
            """,
            (orden_id,),
        ).fetchone()

        if orden is None:
            raise ValueError("La OT no existe.")

        if orden["estado"] not in {
            "pendiente",
            "pausada",
        }:
            raise ValueError("Solo se pueden mover OT pendientes o pausadas.")

        tren_origen_id = orden["tren_id"]

        if tren_origen_id == tren_destino_id:
            raise ValueError("La OT ya pertenece al tren seleccionado.")

        if orden["estado"] == "pendiente":
            ultima_posicion = conexion.execute(
                """
                SELECT COALESCE(MAX(posicion), 0)
                FROM ordenes
                WHERE tren_id = ?
                  AND estado IN (
                      'pendiente',
                      'en_produccion'
                  )
                """,
                (tren_destino_id,),
            ).fetchone()[0]

            conexion.execute(
                """
                UPDATE ordenes
                SET
                    tren_id = ?,
                    posicion = ?
                WHERE id = ?
                """,
                (
                    tren_destino_id,
                    ultima_posicion + 1,
                    orden_id,
                ),
            )

        else:
            conexion.execute(
                """
                UPDATE ordenes
                SET
                    tren_id = ?,
                    posicion = NULL
                WHERE id = ?
                """,
                (
                    tren_destino_id,
                    orden_id,
                ),
            )

    reorganizar_posiciones(tren_origen_id)

    registrar_movimiento_orden(
        orden_id=orden_id,
        tren_origen_id=tren_origen_id,
        tren_destino_id=tren_destino_id,
    )
