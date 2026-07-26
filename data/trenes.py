from data.conexion import obtener_conexion


def obtener_trenes_activos() -> list[dict]:
    """
    Devuelve los trenes activos en el orden configurado.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT
                id,
                nombre,
                descripcion,
                orden_visual,
                posiciones_ojos,
                costura_visible,
                costura_invisible,
                costura_reforzada
            FROM trenes
            WHERE activo = 1
            ORDER BY orden_visual ASC, id ASC
            """
        ).fetchall()

    return [dict(fila) for fila in filas]


def obtener_tren(
    tren_id: int,
) -> dict | None:
    """
    Devuelve un tren por su identificador.
    """
    with obtener_conexion() as conexion:
        fila = conexion.execute(
            """
            SELECT
                id,
                nombre,
                descripcion,
                activo,
                orden_visual,
                posiciones_ojos,
                costura_visible,
                costura_invisible,
                costura_reforzada
            FROM trenes
            WHERE id = ?
            """,
            (tren_id,),
        ).fetchone()

    if fila is None:
        return None

    return dict(fila)