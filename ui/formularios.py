import sqlite3
from datetime import date, datetime, time

import streamlit as st

from core.programacion import ajustar_inicio_laboral
from data.estado_tren import (
    definir_inicio_programacion,
    obtener_estado_tren,
)
from data.ordenes import agregar_orden
from ui.mensajes import (
    guardar_mensaje,
    guardar_mensaje_general,
)


def mostrar_formulario_inicio_programacion() -> datetime | None:
    """
    Muestra el formulario para definir el inicio de una
    nueva programación.

    Si ya existe una programación activa, devuelve el
    próximo inicio guardado.
    """
    estado_tren = obtener_estado_tren()

    if not estado_tren["programacion_activa"]:
        st.subheader("Inicio de nueva programación")

        st.info("Define cuándo debe comenzar la primera OT de esta nueva secuencia.")

        with st.form("formulario_inicio_programacion"):
            columna_fecha, columna_hora = st.columns(2)

            with columna_fecha:
                fecha_inicio = st.date_input(
                    "Fecha de inicio",
                    value=date.today(),
                    format="DD/MM/YYYY",
                )

            with columna_hora:
                hora_inicio = st.time_input(
                    "Hora de inicio",
                    value=time(hour=6, minute=0),
                    step=900,
                )

            confirmar_inicio = st.form_submit_button(
                "Definir inicio de programación",
                type="primary",
                use_container_width=True,
            )

        if confirmar_inicio:
            inicio_seleccionado = datetime.combine(
                fecha_inicio,
                hora_inicio,
            )

            inicio_ajustado = ajustar_inicio_laboral(inicio_seleccionado)

            definir_inicio_programacion(inicio_ajustado)

            if inicio_ajustado != inicio_seleccionado:
                guardar_mensaje_general(
                    "La hora seleccionada estaba fuera del "
                    "horario laboral. El inicio fue ajustado al "
                    f"{inicio_ajustado.strftime('%d/%m/%Y %H:%M')}."
                )

            else:
                guardar_mensaje_general(
                    "El inicio de programación fue guardado correctamente."
                )

            st.rerun()

        return None

    proximo_inicio_guardado = estado_tren["proximo_inicio"]

    if not proximo_inicio_guardado:
        st.error(
            "La programación figura como activa, pero no tiene "
            "una fecha de inicio guardada."
        )

        return None

    try:
        inicio_programacion = datetime.fromisoformat(proximo_inicio_guardado)

    except ValueError:
        st.error("La fecha de inicio guardada no tiene un formato válido.")

        return None

    st.info(
        "Inicio actual de la programación: "
        f"**{inicio_programacion.strftime('%d/%m/%Y %H:%M')}**"
    )

    return inicio_programacion


def mostrar_formulario_nueva_ot() -> None:
    """
    Muestra el formulario para añadir una nueva OT.
    """
    st.subheader("Añadir OT")

    with st.form(
        "formulario_orden",
        clear_on_submit=True,
    ):
        columna_ot, columna_duracion = st.columns(2)

        with columna_ot:
            numero_ot = st.text_input(
                "Número de OT",
                placeholder="Ejemplo: OT-1001",
            )

        with columna_duracion:
            duracion_horas = st.number_input(
                "Duración en horas",
                min_value=0.25,
                value=1.0,
                step=0.25,
            )

        guardar = st.form_submit_button(
            "Añadir OT",
            type="primary",
            use_container_width=True,
        )

    if not guardar:
        return

    if not numero_ot.strip():
        st.error("Debes escribir el número de OT.")

        return

    try:
        agregar_orden(
            numero_ot=numero_ot,
            duracion_horas=duracion_horas,
        )

        guardar_mensaje(f"La OT {numero_ot.strip()} fue añadida.")

        st.rerun()

    except sqlite3.IntegrityError:
        st.error("Ya existe una OT con ese número.")

    except sqlite3.Error as error:
        st.error(f"No fue posible añadir la OT: {error}")
