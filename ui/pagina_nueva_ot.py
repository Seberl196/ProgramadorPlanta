import streamlit as st

from data.trenes import obtener_trenes_activos
from ui.formularios import mostrar_formulario_nueva_ot


def mostrar_pagina_nueva_ot() -> None:
    """
    Muestra la página global para crear una nueva OT.
    """
    st.header("Nueva orden de trabajo")

    trenes = obtener_trenes_activos()

    if not trenes:
        st.warning("No hay trenes activos disponibles.")
        return

    opciones = {
        tren["nombre"]: tren["id"]
        for tren in trenes
    }

    nombre_tren = st.selectbox(
        "Tren",
        opciones.keys(),
    )

    tren_id = opciones[nombre_tren]

    mostrar_formulario_nueva_ot(
        tren_id=tren_id,
    )