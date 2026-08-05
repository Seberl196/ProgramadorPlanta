import streamlit as st

from data.consultas_ordenes import buscar_ordenes_historial
from data.trenes import obtener_trenes_activos
from ui.historial_produccion import mostrar_historial_produccion


def mostrar_pagina_historial() -> None:
    """
    Muestra el historial global de órdenes de trabajo.
    """
    st.header("Historial de órdenes de trabajo")

    trenes = obtener_trenes_activos()

    opciones_trenes = {
        "Todos": None,
    }

    opciones_trenes.update({tren["nombre"]: tren["id"] for tren in trenes})

    opciones_estados = {
        "Todos": None,
        "Entrada": "entrada",
        "Pendiente": "pendiente",
        "En producción": "en_produccion",
        "Pausada": "pausada",
        "Terminada": "terminada",
    }

    columna_tren, columna_estado, columna_ot = st.columns(3)

    with columna_tren:
        nombre_tren = st.selectbox(
            "Tren",
            opciones_trenes.keys(),
            key="historial_tren",
        )

    with columna_estado:
        nombre_estado = st.selectbox(
            "Estado",
            opciones_estados.keys(),
            key="historial_estado",
        )

    with columna_ot:
        numero_ot = st.text_input(
            "Número de OT",
            placeholder="Buscar OT...",
            key="historial_numero_ot",
        )

    ordenes = buscar_ordenes_historial(
        tren_id=opciones_trenes[nombre_tren],
        numero_ot=numero_ot,
        estado=opciones_estados[nombre_estado],
    )

    mostrar_historial_produccion(
        ordenes=ordenes,
    )
