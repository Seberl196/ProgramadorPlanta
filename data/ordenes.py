from datetime import datetime

from data.conexion import obtener_conexion


def obtener_ordenes() -> list[dict]:
    """
    Devuelve todas las OT no terminadas.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT *
            FROM ordenes
            WHERE estado != 'terminada'
            ORDER BY posicion ASC, id ASC
            """
        ).fetchall()

    return [dict(fila) for fila in filas]


def obtener_ordenes_programables() -> list[dict]:
    """
    Devuelve la cola activa del tren.

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
            ORDER BY posicion ASC, id ASC
            """
        ).fetchall()

    return [dict(fila) for fila in filas]


def obtener_ordenes_pausadas() -> list[dict]:
    """
    Devuelve las OT pausadas.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT *
            FROM ordenes
            WHERE estado = 'pausada'
            ORDER BY id ASC
            """
        ).fetchall()

    return [dict(fila) for fila in filas]


def obtener_historial() -> list[dict]:
    """
    Devuelve las OT terminadas.
    """
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            """
            SELECT *
            FROM ordenes
            WHERE estado = 'terminada'
            ORDER BY fecha_fin_real DESC, id DESC
            """
        ).fetchall()

    return [dict(fila) for fila in filas]


def agregar_orden(
    numero_ot: str,
    duracion_horas: float,
) -> None:
    """
    Añade una OT al final de la cola activa.
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
            """
        ).fetchone()

        conexion.execute(
            """
            INSERT INTO ordenes (
                posicion,
                numero_ot,
                duracion_horas,
                estado,
                horas_producidas
            )
            VALUES (?, ?, ?, 'pendiente', 0)
            """,
            (
                int(resultado["siguiente_posicion"]),
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

    ordenes = obtener_ordenes_programables()

    indice_actual = next(
        (indice for indice, orden in enumerate(ordenes) if orden["id"] == orden_id),
        None,
    )

    if indice_actual is None:
        return

    orden_actual = ordenes[indice_actual]

    if orden_actual["estado"] != "pendiente":
        return

    desplazamiento = -1 if direccion == "subir" else 1

    indice_vecino = indice_actual + desplazamiento

    if not 0 <= indice_vecino < len(ordenes):
        return

    orden_vecina = ordenes[indice_vecino]

    if orden_vecina["estado"] != "pendiente":
        return

    with obtener_conexion() as conexion:
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


def eliminar_orden(
    orden_id: int,
) -> None:
    """
    Elimina una OT pendiente.
    """
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            DELETE FROM ordenes
            WHERE id = ?
              AND estado = 'pendiente'
            """,
            (orden_id,),
        )

    reorganizar_posiciones()


def reorganizar_posiciones() -> None:
    """
    Reorganiza únicamente la cola activa.
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
            ORDER BY posicion ASC, id ASC
            """
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


def iniciar_produccion(
    orden_id: int,
) -> None:
    """
    Inicia la primera OT pendiente.
    """
    with obtener_conexion() as conexion:
        primera = conexion.execute(
            """
            SELECT id
            FROM ordenes
            WHERE estado = 'pendiente'
            ORDER BY posicion ASC, id ASC
            LIMIT 1
            """
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
            LIMIT 1
            """
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
            (orden_id,),
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
            WHERE id = 1
            """,
            (proximo_inicio.isoformat(),),
        )

    reorganizar_posiciones()


def reanudar_produccion(
    orden_id: int,
) -> None:
    """
    Reanuda una OT pausada y la coloca al frente.
    """
    with obtener_conexion() as conexion:
        orden = conexion.execute(
            """
            SELECT id, estado
            FROM ordenes
            WHERE id = ?
            """,
            (orden_id,),
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
            LIMIT 1
            """
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
            """
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

    reorganizar_posiciones()


def terminar_produccion(
    orden_id: int,
    fecha_fin_real: datetime,
    proximo_inicio: datetime,
) -> None:
    """
    Finaliza una OT y actualiza el próximo inicio
    disponible del tren.
    """
    fecha_fin_texto = fecha_fin_real.isoformat()

    proximo_inicio_texto = proximo_inicio.isoformat()

    with obtener_conexion() as conexion:
        orden = conexion.execute(
            """
            SELECT id, estado
            FROM ordenes
            WHERE id = ?
            """,
            (orden_id,),
        ).fetchone()

        if orden is None:
            raise ValueError("La OT seleccionada no existe.")

        if orden["estado"] not in {
            "en_produccion",
            "pausada",
        }:
            raise ValueError("Solo se puede terminar una OT en producción o pausada.")

        conexion.execute(
            """
            UPDATE ordenes
            SET
                estado = 'terminada',
                fecha_fin_real = ?
            WHERE id = ?
            """,
            (
                fecha_fin_texto,
                orden_id,
            ),
        )

        resultado = conexion.execute(
            """
            SELECT COUNT(*) AS cantidad
            FROM ordenes
            WHERE estado != 'terminada'
            """
        ).fetchone()

        ordenes_activas = int(resultado["cantidad"])

        if ordenes_activas > 0:
            conexion.execute(
                """
                UPDATE estado_tren
                SET
                    proximo_inicio = ?,
                    programacion_activa = 1
                WHERE id = 1
                """,
                (proximo_inicio_texto,),
            )

        else:
            conexion.execute(
                """
                UPDATE estado_tren
                SET
                    proximo_inicio = NULL,
                    programacion_activa = 0
                WHERE id = 1
                """
            )

    reorganizar_posiciones()
