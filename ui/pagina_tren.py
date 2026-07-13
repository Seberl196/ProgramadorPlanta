import streamlit as st

from ui.formularios import (
    mostrar_formulario_inicio_programacion,
    mostrar_formulario_nueva_ot,
)
from ui.gantt import mostrar_gantt
from ui.tarjetas import mostrar_programacion
from ui.gantt_diario import mostrar_gantt_diario


def mostrar_pagina_tren(
    numero_tren: int,
) -> None:
    """
    Muestra la página completa de un tren con dos vistas:

    - Kanban para gestionar la producción.
    - Gantt para visualizar la programación.
    """
    st.header(f"Programación — Tren {numero_tren}")

    st.caption("Horario de producción: todos los días de 06:00 a 22:00.")

    inicio_programacion = mostrar_formulario_inicio_programacion()

    pestana_kanban, pestana_gantt_1, pestana_gantt_2 = st.tabs(
        [
            "Kanban",
            "Gantt 1",
            "Gantt 2",
        ]
    )

    with pestana_kanban:
        mostrar_formulario_nueva_ot()

        st.divider()

        mostrar_programacion(inicio_programacion)

    with pestana_gantt_1:
        mostrar_gantt(inicio_programacion)

    with pestana_gantt_2:
        mostrar_gantt_diario(inicio_programacion)
