import streamlit as st

from ui.formularios import (
    mostrar_formulario_inicio_programacion,
)
from ui.gantt import mostrar_gantt
from ui.gantt_diario import mostrar_gantt_diario
from ui.historial_produccion import mostrar_historial_produccion
from ui.tarjetas import mostrar_programacion


def mostrar_pagina_tren(
    tren_id: int,
    nombre_tren: str,
) -> None:
    """
    Muestra la página completa del tren seleccionado.

    Incluye:

    - Kanban para gestionar la producción.
    - Gantt general.
    - Gantt diario.
    - Historial de producción.
    """
    st.header(f"Programación — {nombre_tren}")

    st.caption("Horario de producción: todos los días de 06:00 a 22:00.")

    inicio_programacion = mostrar_formulario_inicio_programacion(
        tren_id=tren_id,
    )

    pestana_kanban, pestana_gantt_1, pestana_gantt_2, pestana_historial = st.tabs(
        [
            "Kanban",
            "Gantt 1",
            "Gantt 2",
            "Historial",
        ]
    )

    with pestana_kanban:

        mostrar_programacion(
            inicio_programacion,
            tren_id=tren_id,
        )

    with pestana_gantt_1:
        mostrar_gantt(
            inicio_programacion,
            tren_id=tren_id,
        )

    with pestana_gantt_2:
        mostrar_gantt_diario(
            inicio_programacion,
            tren_id=tren_id,
        )

    with pestana_historial:
        mostrar_historial_produccion(
            tren_id=tren_id,
        )
