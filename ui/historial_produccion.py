import streamlit as st

from data.historial_produccion import obtener_historial_produccion


def mostrar_historial_produccion(
    tren_id: int,
) -> None:
    """
    Muestra el historial de producción del tren.
    """
    historial = obtener_historial_produccion(tren_id)

    st.subheader("Historial de producción")

    if not historial:
        st.info("Todavía no hay eventos registrados para este tren.")
        return

    for evento in historial:
        st.write(
            f"OT {evento['numero_ot']} · "
            f"{evento['evento']} · "
            f"{evento['fecha_hora']} · "
            f"Horas producidas: {evento['horas_producidas']}"
        )