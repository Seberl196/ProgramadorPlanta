import streamlit as st


def inicializar_mensajes() -> None:
    """
    Crea las variables de sesión utilizadas
    para mostrar notificaciones.
    """
    if "mensaje" not in st.session_state:
        st.session_state.mensaje = None

    if "mensaje_icono" not in st.session_state:
        st.session_state.mensaje_icono = "✅"

    if "mensaje_general" not in st.session_state:
        st.session_state.mensaje_general = None


def guardar_mensaje(
    texto: str,
    icono: str = "✅",
) -> None:
    """
    Guarda un mensaje para mostrarlo después
    de la siguiente recarga de Streamlit.
    """
    st.session_state.mensaje = texto
    st.session_state.mensaje_icono = icono


def guardar_mensaje_general(texto: str) -> None:
    """
    Guarda un mensaje general de la aplicación.
    """
    st.session_state.mensaje_general = texto


def mostrar_mensajes() -> None:
    """
    Muestra los mensajes pendientes y luego los limpia.
    """
    if st.session_state.mensaje:
        st.toast(
            st.session_state.mensaje,
            icon=st.session_state.mensaje_icono,
        )

        st.session_state.mensaje = None

    if st.session_state.mensaje_general:
        st.toast(
            st.session_state.mensaje_general,
            icon="✅",
        )

        st.session_state.mensaje_general = None
