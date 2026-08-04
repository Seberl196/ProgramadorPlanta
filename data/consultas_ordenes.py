from data.conexion import obtener_conexion


def obtener_tren_id_de_orden(
    orden_id: int,
) -> int:
    """
    Obtiene el tren al que pertenece una OT.
    """
    with obtener_conexion() as conexion:
        fila = conexion.execute(
            """
            SELECT tren_id
            FROM ordenes
            WHERE id = ?
            """,
            (orden_id,),
        ).fetchone()

    if fila is None:
        raise ValueError("La OT seleccionada no existe.")

    return int(fila["tren_id"])


def obtener_ordenes(
    tren_id: int,
) -> list[dict]:
    """
    Devuelve todas las OT no terminadas
    del tren indicado.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT *
            FROM ordenes
            WHERE estado != 'terminada'
              AND tren_id = ?
            ORDER BY posicion ASC, id ASC
            """,
            (tren_id,),
        ).fetchall()

    return [dict(fila) for fila in filas]


def obtener_ordenes_programables(
    tren_id: int,
) -> list[dict]:
    """
    Devuelve la cola activa del tren indicado.

    Las OT pausadas quedan fuera de esta cola.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT *
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

    return [dict(fila) for fila in filas]


def obtener_ordenes_pausadas(
    tren_id: int,
) -> list[dict]:
    """
    Devuelve las OT pausadas del tren indicado.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT *
            FROM ordenes
            WHERE estado = 'pausada'
              AND tren_id = ?
            ORDER BY id ASC
            """,
            (tren_id,),
        ).fetchall()

    return [dict(fila) for fila in filas]


def obtener_historial(
    tren_id: int,
) -> list[dict]:
    """
    Devuelve las OT terminadas del tren indicado.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT *
            FROM ordenes
            WHERE estado = 'terminada'
              AND tren_id = ?
            ORDER BY fecha_fin_real DESC, id DESC
            """,
            (tren_id,),
        ).fetchall()

    return [dict(fila) for fila in filas]


def obtener_ordenes_entrada() -> list[dict]:
    """
    Obtiene las OT que todavía no han sido asignadas a un tren.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT
                id,
                numero_ot,
                duracion_horas,
                estado
            FROM ordenes
            WHERE estado = 'entrada'
            ORDER BY id ASC
            """
        ).fetchall()

    return [dict(fila) for fila in filas]


def buscar_historial(
    tren_id: int | None = None,
    numero_ot: str | None = None,
) -> list[dict]:
    """
    Busca OT terminadas filtrando opcionalmente
    por tren y número de OT.
    """
    consulta = """
        SELECT *
        FROM ordenes
        WHERE estado = 'terminada'
    """

    parametros = []

    if tren_id is not None:
        consulta += """
            AND tren_id = ?
        """
        parametros.append(tren_id)

    if numero_ot:
        consulta += """
            AND numero_ot LIKE ?
        """
        parametros.append(f"%{numero_ot.strip()}%")

    consulta += """
        ORDER BY fecha_fin_real DESC, id DESC
    """

    with obtener_conexion() as conexion:
        filas = conexion.execute(
            consulta,
            parametros,
        ).fetchall()

    return [dict(fila) for fila in filas]
