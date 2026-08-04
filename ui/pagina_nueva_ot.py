import streamlit as st

from data.consultas_ordenes import obtener_ordenes_entrada
from ui.formularios import mostrar_formulario_nueva_ot
from data.ordenes import asignar_orden_a_tren
from data.trenes import obtener_trenes_activos


def mostrar_pagina_nueva_ot() -> None:
    """
    Muestra la creación de OT y las OT pendientes de asignación.
    """
    st.header("Órdenes de trabajo")

    st.caption(
        "Las nuevas OT se guardan sin tren asignado "
        "hasta que sean programadas."
    )

    mostrar_formulario_nueva_ot()

    st.divider()

    st.subheader("Pendientes de asignación")

    ordenes = obtener_ordenes_entrada()
    trenes = obtener_trenes_activos()

    if not ordenes:
        st.info("No hay órdenes de trabajo pendientes de asignación.")
        return

    for orden in ordenes:
        with st.container(border=True):
            columna_info, columna_tren, columna_accion = st.columns(
                [2, 2, 1]
            )

            with columna_info:
                st.write(f"**OT {orden['numero_ot']}**")
                st.write(
                    f"Duración: {orden['duracion_horas']:.2f} h"
                )

            with columna_tren:
                opciones_trenes = {
                    tren["nombre"]: tren["id"]
                    for tren in trenes
                }

                nombre_tren = st.selectbox(
                    "Tren destino",
                    opciones_trenes.keys(),
                    key=f"tren_destino_{orden['id']}",
                )

            with columna_accion:
                st.write("")

                if st.button(
                    "Asignar",
                    key=f"asignar_{orden['id']}",
                    type="primary",
                    use_container_width=True,
                ):
                    asignar_orden_a_tren(
                        orden_id=orden["id"],
                        tren_id=opciones_trenes[nombre_tren],
                    )

                    st.rerun()