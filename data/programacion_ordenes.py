from data.conexion import obtener_conexion


def mover_orden(
    orden_id: int,
    direccion: str,
) -> None:
    """
    Mueve una OT pendiente una posición.
    """
    if direccion not in {
        "subir",
        "bajar",
    }:
        raise ValueError("La dirección debe ser 'subir' o 'bajar'.")

    with obtener_conexion() as conexion:
        orden_actual = conexion.execute(
            """
            SELECT
                id,
                posicion,
                estado,
                tren_id
            FROM ordenes
            WHERE id = ?
            """,
            (orden_id,),
        ).fetchone()

        if orden_actual is None:
            raise ValueError("La OT seleccionada no existe.")

        if orden_actual["estado"] != "pendiente":
            return

        direccion_sql = "DESC" if direccion == "subir" else "ASC"

        comparador = "<" if direccion == "subir" else ">"

        orden_vecina = conexion.execute(
            f"""
            SELECT
                id,
                posicion,
                estado
            FROM ordenes
            WHERE tren_id = ?
              AND estado = 'pendiente'
              AND posicion {comparador} ?
            ORDER BY posicion {direccion_sql}, id {direccion_sql}
            LIMIT 1
            """,
            (
                orden_actual["tren_id"],
                orden_actual["posicion"],
            ),
        ).fetchone()

        if orden_vecina is None:
            return

        conexion.execute(
            """
            UPDATE ordenes
            SET posicion = ?
            WHERE id = ?
            """,
            (
                orden_vecina["posicion"],
                orden_actual["id"],
            ),
        )

        conexion.execute(
            """
            UPDATE ordenes
            SET posicion = ?
            WHERE id = ?
            """,
            (
                orden_actual["posicion"],
                orden_vecina["id"],
            ),
        )


def reorganizar_posiciones(
    tren_id: int,
) -> None:
    """
    Reorganiza únicamente la cola activa
    del tren indicado.
    """
    with obtener_conexion() as conexion:
        ordenes = conexion.execute(
            """
            SELECT id
            FROM ordenes
            WHERE estado IN (
                'pendiente',
                'en_produccion'
            )
              AND tren_id = ?
            ORDER BY posicion ASC, id ASC
            """,
            (tren_id,),
        ).fetchall()

        for nueva_posicion, orden in enumerate(
            ordenes,
            start=1,
        ):
            conexion.execute(
                """
                UPDATE ordenes
                SET posicion = ?
                WHERE id = ?
                """,
                (
                    nueva_posicion,
                    orden["id"],
                ),
            )
