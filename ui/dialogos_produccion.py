import sqlite3
from datetime import datetime

import streamlit as st

from core.programacion import ajustar_inicio_laboral
from data.ordenes import (
    pausar_produccion,
    terminar_produccion,
)
from ui.mensajes import guardar_mensaje


@st.dialog("Pausar producción")
def mostrar_dialogo_pausa(
    orden: dict,
) -> None:
    """
    Registra el avance de una OT antes de pausarla
    y libera el tren para la siguiente orden.
    """
    duracion_total = float(orden["duracion_horas"])

    avance_actual = float(orden.get("horas_producidas") or 0)

    st.write(f"Registra el avance actual de la OT **{orden['numero_ot']}**.")

    st.write(f"**Duración total:** {duracion_total:.2f} horas")

    horas_producidas = st.number_input(
        "Horas producidas hasta el momento",
        min_value=0.0,
        max_value=duracion_total,
        value=avance_actual,
        step=0.25,
        key=f"avance_pausa_{orden['id']}",
    )

    horas_restantes = max(
        duracion_total - horas_producidas,
        0,
    )

    st.info(f"Tiempo restante estimado: **{horas_restantes:.2f} horas**")

    momento_pausa_real = datetime.now().replace(
        second=0,
        microsecond=0,
    )

    inicio_siguiente_ot = ajustar_inicio_laboral(momento_pausa_real)

    st.info(
        "El Tren 1 quedará disponible desde: "
        f"**{inicio_siguiente_ot.strftime('%d/%m/%Y %H:%M')}**"
    )

    confirmar, cancelar = st.columns(2)

    with confirmar:
        if st.button(
            "Confirmar pausa",
            type="primary",
            use_container_width=True,
            key=f"confirmar_pausa_{orden['id']}",
        ):
            try:
                pausar_produccion(
                    orden_id=orden["id"],
                    horas_producidas=horas_producidas,
                    proximo_inicio=inicio_siguiente_ot,
                )

                guardar_mensaje(
                    f"La OT {orden['numero_ot']} fue pausada "
                    f"con {horas_producidas:.2f} horas "
                    "producidas.",
                    "⏸️",
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except sqlite3.Error as error:
                st.error(f"No fue posible pausar la OT: {error}")

    with cancelar:
        if st.button(
            "Cancelar",
            use_container_width=True,
            key=f"cancelar_pausa_{orden['id']}",
        ):
            st.rerun()


@st.dialog("Terminar producción")
def mostrar_dialogo_terminar(
    orden: dict,
) -> None:
    """
    Registra la fecha y hora real de finalización
    de una OT.
    """
    st.write(
        "Registra la fecha y hora real de finalización "
        f"de la OT **{orden['numero_ot']}**."
    )

    ahora = datetime.now()

    columna_hora, columna_fecha = st.columns(2)

    with columna_hora:
        hora_finalizacion = st.time_input(
            "Hora de finalización",
            value=ahora.time().replace(
                second=0,
                microsecond=0,
            ),
            step=300,
            key=f"hora_fin_{orden['id']}",
        )

    with columna_fecha:
        fecha_finalizacion = st.date_input(
            "Fecha de finalización",
            value=ahora.date(),
            format="DD/MM/YYYY",
            key=f"fecha_fin_{orden['id']}",
        )

    fin_real = datetime.combine(
        fecha_finalizacion,
        hora_finalizacion,
    )

    inicio_siguiente_ot = ajustar_inicio_laboral(fin_real)

    if inicio_siguiente_ot == fin_real:
        st.info(
            "La siguiente OT comenzará el "
            f"**{inicio_siguiente_ot.strftime('%d/%m/%Y %H:%M')}**."
        )

    else:
        st.warning(
            "La finalización está fuera del horario laboral. "
            "La siguiente OT comenzará el "
            f"**{inicio_siguiente_ot.strftime('%d/%m/%Y %H:%M')}**."
        )

    confirmar, cancelar = st.columns(2)

    with confirmar:
        if st.button(
            "Sí, terminar",
            type="primary",
            use_container_width=True,
            key=f"confirmar_terminar_{orden['id']}",
        ):
            try:
                terminar_produccion(
                    orden_id=orden["id"],
                    fecha_fin_real=fin_real,
                    proximo_inicio=inicio_siguiente_ot,
                )

                guardar_mensaje(
                    f"La OT {orden['numero_ot']} terminó el "
                    f"{fin_real.strftime('%d/%m/%Y %H:%M')}.",
                    "🏁",
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except sqlite3.Error as error:
                st.error(f"No fue posible terminar la OT: {error}")

    with cancelar:
        if st.button(
            "Cancelar",
            use_container_width=True,
            key=f"cancelar_terminar_{orden['id']}",
        ):
            st.rerun()
