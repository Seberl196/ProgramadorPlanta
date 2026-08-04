import streamlit as st

from data.consultas_ordenes import buscar_historial
from data.trenes import obtener_trenes_activos
from ui.historial_produccion import mostrar_historial_produccion


def mostrar_pagina_historial() -> None:
    """
    Muestra el historial global de producción.
    """
    st.header("Historial de producción")

    trenes = obtener_trenes_activos()

    opciones_trenes = {
        "Todos": None,
    }

    opciones_trenes.update({tren["nombre"]: tren["id"] for tren in trenes})

    columna_tren, columna_ot = st.columns(2)

    with columna_tren:
        nombre_tren = st.selectbox(
            "Tren",
            opciones_trenes.keys(),
            key="historial_tren",
        )

    with columna_ot:
        numero_ot = st.text_input(
            "Número de OT",
            placeholder="Buscar OT...",
        )

    ordenes = buscar_historial(
        tren_id=opciones_trenes[nombre_tren],
        numero_ot=numero_ot,
    )

    mostrar_historial_produccion(
        ordenes=ordenes,
    )
