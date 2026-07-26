import streamlit as st

from core.inicializacion import inicializar_aplicacion
from ui.estilos import cargar_estilos
from ui.mensajes import (
    inicializar_mensajes,
    mostrar_mensajes,
)
from ui.pagina_tren import mostrar_pagina_tren
from data.trenes import obtener_trenes_activos


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


if not trenes:
    st.error("No hay trenes activos configurados.")
    st.stop()

opciones_trenes = {
    tren["nombre"]: tren["id"]
    for tren in trenes
}

nombre_tren_seleccionado = st.selectbox(
    "Tren de producción",
    options=list(opciones_trenes.keys()),
    key="tren_seleccionado",
)

tren_id_seleccionado = opciones_trenes[
    nombre_tren_seleccionado
]

mostrar_pagina_tren(
    tren_id=tren_id_seleccionado,
    nombre_tren=nombre_tren_seleccionado,
)
