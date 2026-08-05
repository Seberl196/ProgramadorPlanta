import sqlite3
from datetime import datetime

import streamlit as st

from core.programacion import ajustar_inicio_laboral
from data.ordenes import (
    actualizar_orden,
    eliminar_orden,
)
from ui.mensajes import guardar_mensaje
from data.ordenes import (
    actualizar_orden,
    eliminar_orden,
    mover_orden_a_tren,
)
from data.trenes import obtener_trenes_activos

@st.dialog("Editar orden de trabajo")
def mostrar_dialogo_edicion(
    orden: dict,
) -> None:
    """
    Permite editar:

    - Número de OT.
    - Duración.
    - Inicio programado opcional.
    """
    st.caption(f"Editando la OT {orden['numero_ot']}")

    inicio_manual_guardado = None

    if orden.get("inicio_manual"):
        try:
            inicio_manual_guardado = datetime.fromisoformat(orden["inicio_manual"])

        except (TypeError, ValueError):
            inicio_manual_guardado = None

    nuevo_numero_ot = st.text_input(
        "Número de OT",
        value=orden["numero_ot"],
        key=f"editar_numero_ot_{orden['id']}",
    )

    nueva_duracion = st.number_input(
        "Duración en horas",
        min_value=0.25,
        value=float(orden["duracion_horas"]),
        step=0.25,
        key=f"editar_duracion_{orden['id']}",
    )

    st.divider()

    usar_inicio_manual = st.checkbox(
        "Definir un inicio programado para esta OT",
        value=(inicio_manual_guardado is not None),
        key=f"usar_inicio_manual_{orden['id']}",
    )

    nueva_fecha_inicio = None
    nueva_hora_inicio = None

    if usar_inicio_manual:
        valor_inicial = inicio_manual_guardado or datetime.now().replace(
            second=0,
            microsecond=0,
        )

        columna_fecha, columna_hora = st.columns(2)

        with columna_fecha:
            nueva_fecha_inicio = st.date_input(
                "Fecha de inicio programado",
                value=valor_inicial.date(),
                format="DD/MM/YYYY",
                key=f"fecha_inicio_manual_{orden['id']}",
            )

        with columna_hora:
            nueva_hora_inicio = st.time_input(
                "Hora de inicio programado",
                value=valor_inicial.time(),
                step=900,
                key=f"hora_inicio_manual_{orden['id']}",
            )

        inicio_seleccionado = datetime.combine(
            nueva_fecha_inicio,
            nueva_hora_inicio,
        )

        inicio_ajustado = ajustar_inicio_laboral(inicio_seleccionado)

        if inicio_ajustado != inicio_seleccionado:
            st.warning(
                "La hora seleccionada está fuera del horario "
                "laboral. Se ajustará al "
                f"**{inicio_ajustado.strftime('%d/%m/%Y %H:%M')}**."
            )

        else:
            st.info(
                "La OT no comenzará antes del "
                f"**{inicio_ajustado.strftime('%d/%m/%Y %H:%M')}**."
            )

    columna_guardar, columna_cancelar = st.columns(2)

    with columna_guardar:
        guardar = st.button(
            "Guardar cambios",
            type="primary",
            use_container_width=True,
            key=f"guardar_edicion_{orden['id']}",
        )

    with columna_cancelar:
        cancelar = st.button(
            "Cancelar",
            use_container_width=True,
            key=f"cancelar_edicion_{orden['id']}",
        )

    if cancelar:
        st.rerun()

    if not guardar:
        return

    if not nuevo_numero_ot.strip():
        st.error("Debes escribir el número de OT.")
        return

    nuevo_inicio_manual = None

    if usar_inicio_manual:
        nuevo_inicio_manual = datetime.combine(
            nueva_fecha_inicio,
            nueva_hora_inicio,
        )

        nuevo_inicio_manual = ajustar_inicio_laboral(nuevo_inicio_manual)

    try:
        actualizar_orden(
            orden_id=orden["id"],
            numero_ot=nuevo_numero_ot,
            duracion_horas=nueva_duracion,
            inicio_manual=nuevo_inicio_manual,
        )

        guardar_mensaje(f"La OT {nuevo_numero_ot.strip()} fue actualizada.")

        st.rerun()

    except sqlite3.IntegrityError:
        st.error("Ya existe otra OT con ese número.")

    except sqlite3.Error as error:
        st.error(f"No fue posible actualizar la OT: {error}")


@st.dialog("Eliminar orden de trabajo")
def mostrar_dialogo_eliminacion(
    orden: dict,
) -> None:
    """
    Solicita confirmación antes de eliminar una OT.
    """
    st.warning(f"¿Estás seguro de que deseas eliminar la OT **{orden['numero_ot']}**?")

    st.write("Esta acción no se puede deshacer.")

    confirmar, cancelar = st.columns(2)

    with confirmar:
        if st.button(
            "Sí, eliminar",
            type="primary",
            use_container_width=True,
            key=f"confirmar_eliminar_{orden['id']}",
        ):
            try:
                eliminar_orden(orden["id"])

                guardar_mensaje(
                    f"La OT {orden['numero_ot']} fue eliminada.",
                    "🗑️",
                )

                st.rerun()

            except sqlite3.Error as error:
                st.error(f"No fue posible eliminar la OT: {error}")

    with cancelar:
        if st.button(
            "Cancelar",
            use_container_width=True,
            key=f"cancelar_eliminar_{orden['id']}",
        ):
            st.rerun()

@st.dialog("Mover orden de trabajo")
def mostrar_dialogo_mover(
    orden: dict,
) -> None:
    """
    Permite mover una OT pendiente o pausada a otro tren.
    """
    trenes = obtener_trenes_activos()

    trenes_destino = [
        tren
        for tren in trenes
        if tren["id"] != orden["tren_id"]
    ]

    if not trenes_destino:
        st.info("No hay otro tren disponible.")
        return

    st.write(
        f"Selecciona el tren destino para la OT "
        f"**{orden['numero_ot']}**."
    )

    opciones = {
        tren["nombre"]: tren["id"]
        for tren in trenes_destino
    }

    nombre_destino = st.selectbox(
        "Tren destino",
        opciones.keys(),
        key=f"select_tren_destino_{orden['id']}",
    )

    mover, cancelar = st.columns(2)

    with mover:
        if st.button(
            "Mover OT",
            type="primary",
            use_container_width=True,
            key=f"confirmar_mover_{orden['id']}",
        ):
            try:
                mover_orden_a_tren(
                    orden_id=orden["id"],
                    tren_destino_id=opciones[nombre_destino],
                )

                guardar_mensaje(
                    f"La OT {orden['numero_ot']} fue movida a "
                    f"{nombre_destino}.",
                    "↔️",
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except sqlite3.Error as error:
                st.error(
                    f"No fue posible mover la OT: {error}"
                )

    with cancelar:
        if st.button(
            "Cancelar",
            use_container_width=True,
            key=f"cancelar_mover_{orden['id']}",
        ):
            st.rerun()
