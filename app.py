import streamlit as st

from core.inicializacion import inicializar_aplicacion
from ui.estilos import cargar_estilos
from ui.mensajes import (
    inicializar_mensajes,
    mostrar_mensajes,
)
from ui.pagina_tren import mostrar_pagina_tren


st.set_page_config(
    page_title="Programador de Planta",
    page_icon="🏭",
    layout="wide",
)


inicializar_aplicacion()
cargar_estilos()

inicializar_mensajes()
mostrar_mensajes()


st.title("Programador de Planta")


pestanas = st.tabs(
    [
        "Tren 1",
    ]
)


with pestanas[0]:
    mostrar_pagina_tren(numero_tren=1)
