from datetime import datetime

from data.conexion import obtener_conexion
from data.consultas_ordenes import obtener_tren_id_de_orden
from data.programacion_ordenes import reorganizar_posiciones

def iniciar_produccion(
    orden_id: int,
) -> None:
    """
    Inicia la primera OT pendiente.
    """

    tren_id = obtener_tren_id_de_orden(orden_id)

    with obtener_conexion() as conexion:
        primera = conexion.execute(
            """
        SELECT id
        FROM ordenes
        WHERE estado = 'pendiente'
        AND tren_id = ?
        ORDER BY posicion ASC, id ASC
        LIMIT 1
        """,
            (tren_id,),
        ).fetchone()

        if primera is None:
            raise ValueError("No hay una OT pendiente para iniciar.")

        if primera["id"] != orden_id:
            raise ValueError("Solo se puede iniciar la primera OT pendiente.")

        activa = conexion.execute(
            """
            SELECT id
            FROM ordenes
            WHERE estado = 'en_produccion'
            AND tren_id = ?
            LIMIT 1
            """,
            (tren_id,),
        ).fetchone()

        if activa is not None:
            raise ValueError("Ya existe otra OT en producción.")

        conexion.execute(
            """
            UPDATE ordenes
            SET
                estado = 'en_produccion',
                fecha_inicio_real = COALESCE(
                    fecha_inicio_real,
                    ?
                )
            WHERE id = ?
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                orden_id,
            ),
        )


def pausar_produccion(
    orden_id: int,
    horas_producidas: float,
    proximo_inicio: datetime,
) -> None:
    """
    Pausa una OT, guarda el avance y libera el tren.
    """

    tren_id = obtener_tren_id_de_orden(orden_id)

    with obtener_conexion() as conexion:
        orden = conexion.execute(
            """
            SELECT
                id,
                estado,
                duracion_horas,
                horas_producidas
            FROM ordenes
            WHERE id = ?
            """,
            (
                orden_id,
            ),
        ).fetchone()

        if orden is None:
            raise ValueError("La OT seleccionada no existe.")

        if orden["estado"] != "en_produccion":
            raise ValueError("Solo se puede pausar una OT que esté en producción.")

        duracion_total = float(orden["duracion_horas"])

        avance_anterior = float(orden["horas_producidas"] or 0)

        nuevo_avance = float(horas_producidas)

        if nuevo_avance < avance_anterior:
            raise ValueError(
                "El avance no puede ser menor que el registrado anteriormente."
            )

        if nuevo_avance >= duracion_total:
            raise ValueError(
                "El avance debe ser menor que la duración "
                "total. Si la OT terminó, utiliza "
                "'Terminar producción'."
            )

        conexion.execute(
            """
            UPDATE ordenes
            SET
                estado = 'pausada',
                horas_producidas = ?
            WHERE id = ?
            """,
            (
                nuevo_avance,
                orden_id,
            ),
        )

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

    reorganizar_posiciones(tren_id)


def reanudar_produccion(
    orden_id: int,
) -> None:
    """
    Reanuda una OT pausada y la coloca al frente.
    """

    tren_id = obtener_tren_id_de_orden(orden_id)

    with obtener_conexion() as conexion:
        orden = conexion.execute(
            """
            SELECT id, estado
            FROM ordenes
            WHERE id = ?
            """,
            (
                orden_id,
            ),
        ).fetchone()

        if orden is None:
            raise ValueError("La OT seleccionada no existe.")

        if orden["estado"] != "pausada":
            raise ValueError("Solo se puede reanudar una OT pausada.")

        activa = conexion.execute(
            """
            SELECT id
            FROM ordenes
            WHERE estado = 'en_produccion'
            AND tren_id = ?
            LIMIT 1
            """,
            (tren_id,),
        ).fetchone()

        if activa is not None:
            raise ValueError(
                "No se puede reanudar esta OT porque hay otra OT en producción."
            )

        conexion.execute(
            """
            UPDATE ordenes
            SET posicion = posicion + 1
            WHERE estado = 'pendiente'
            AND tren_id = ?
            """,
            (tren_id,),
        )

        conexion.execute(
            """
            UPDATE ordenes
            SET
                estado = 'en_produccion',
                posicion = 1
            WHERE id = ?
            """,
            (orden_id,),
        )

    reorganizar_posiciones(tren_id)


def terminar_produccion(
    orden_id: int,
    fecha_fin_real: datetime,
    proximo_inicio: datetime,
) -> None:
    """
    Termina una OT en producción y actualiza
    el estado de programación del tren indicado.
    """
    tren_id = obtener_tren_id_de_orden(orden_id)
    
    with obtener_conexion() as conexion:
        orden = conexion.execute(
            """
            SELECT
                id,
                estado,
                duracion_horas
            FROM ordenes
            WHERE id = ?
            """,
            (
                orden_id,
            ),
        ).fetchone()

        if orden is None:
            raise ValueError("La OT seleccionada no existe.")

        if orden["estado"] != "en_produccion":
            raise ValueError("Solo se puede terminar una OT que esté en producción.")

        conexion.execute(
            """
            UPDATE ordenes
            SET
                estado = 'terminada',
                fecha_fin_real = ?,
                horas_producidas = duracion_horas
            WHERE id = ?
            """,
            (
                fecha_fin_real.isoformat(),
                orden_id,
            ),
        )

        resultado = conexion.execute(
            """
            SELECT COUNT(*) AS cantidad
            FROM ordenes
            WHERE estado != 'terminada'
              AND tren_id = ?
            """,
            (tren_id,),
        ).fetchone()

        cantidad_ordenes_activas = int(resultado["cantidad"])

        if cantidad_ordenes_activas > 0:
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
        else:
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

    reorganizar_posiciones(tren_id)