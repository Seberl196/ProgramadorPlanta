import streamlit as st

from core.inicializacion import inicializar_aplicacion
from data.trenes import obtener_trenes_activos
from ui.estilos import cargar_estilos
from ui.mensajes import (
    inicializar_mensajes,
    mostrar_mensajes,
)
from ui.pagina_tren import mostrar_pagina_tren
from ui.pagina_nueva_ot import mostrar_pagina_nueva_ot
from ui.pagina_historial import mostrar_pagina_historial

st.set_page_config(
    page_title="Programador de Planta",
    page_icon="🏭",
    layout="wide",
)


inicializar_aplicacion()
cargar_estilos()

inicializar_mensajes()
mostrar_mensajes()

trenes = obtener_trenes_activos()

st.title("Programador de Planta")


trenes = obtener_trenes_activos()

if not trenes:
    st.warning("No hay trenes activos disponibles.")
    st.stop()

if "tren_id_seleccionado" not in st.session_state:
    st.session_state.tren_id_seleccionado = trenes[0]["id"]

if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "tren"

st.sidebar.subheader("Navegación")

if st.sidebar.button(
    "➕ Nueva OT",
    use_container_width=True,
):
    st.session_state.pagina_actual = "nueva_ot"
    st.rerun()

if st.sidebar.button(
    "📋 Historial",
    use_container_width=True,
):
    st.session_state.pagina_actual = "historial"
    st.rerun()

st.sidebar.divider()

st.sidebar.subheader("Trenes")

for tren in trenes:
    if st.sidebar.button(
        tren["nombre"],
        key=f"seleccionar_tren_{tren['id']}",
        use_container_width=True,
    ):
        st.session_state.tren_id_seleccionado = tren["id"]
        st.session_state.pagina_actual = "tren"
        st.rerun()

tren_seleccionado = next(
    tren
    for tren in trenes
    if tren["id"] == st.session_state.tren_id_seleccionado
)

tren_id_seleccionado = tren_seleccionado["id"]
nombre_tren_seleccionado = tren_seleccionado["nombre"]

if st.session_state.pagina_actual == "tren":
    mostrar_pagina_tren(
        tren_id=tren_id_seleccionado,
        nombre_tren=nombre_tren_seleccionado,
    )

elif st.session_state.pagina_actual == "nueva_ot":
    mostrar_pagina_nueva_ot()   

elif st.session_state.pagina_actual == "historial":
    mostrar_pagina_historial()