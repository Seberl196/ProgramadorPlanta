from datetime import datetime

import streamlit as st

from data.consultas_ordenes import obtener_historial
from data.historial_produccion import (
    obtener_eventos_orden,
)


def mostrar_historial_produccion(
    tren_id: int,
) -> None:
    """
    Muestra las OT terminadas del tren y su historial de eventos.
    """
    ordenes = obtener_historial(tren_id)

    st.subheader("Historial de producción")

    if not ordenes:
        st.info("Todavía no hay OT terminadas en este tren.")
        return

    for orden in ordenes:
        fecha_fin = orden.get("fecha_fin_real")

        if fecha_fin:
            fecha_fin_formateada = datetime.fromisoformat(fecha_fin).strftime(
                "%d/%m/%Y %H:%M"
            )
        else:
            fecha_fin_formateada = "Sin fecha"

        titulo = (
            f"OT {orden['numero_ot']} · "
            f"Terminada {fecha_fin_formateada} · "
            f"{orden['duracion_horas']:.2f} h"
        )

        with st.expander(titulo):
            st.write(f"**Duración programada:** {orden['duracion_horas']:.2f} h")

            st.write(f"**Horas producidas:** {orden['horas_producidas']:.2f} h")

            eventos = obtener_eventos_orden(orden["id"])

            if not eventos:
                st.info("Esta OT no tiene eventos registrados en el historial.")
                continue

            st.markdown("#### Eventos")

            for evento in eventos:
                fecha_evento = datetime.fromisoformat(evento["fecha_hora"]).strftime(
                    "%d/%m/%Y %H:%M"
                )

                nombre_evento = evento["evento"].capitalize()

                if evento["horas_producidas"] is None:
                    st.write(f"**{fecha_evento}** · {nombre_evento}")
                else:
                    st.write(
                        f"**{fecha_evento}** · "
                        f"{nombre_evento} · "
                        f"{evento['horas_producidas']:.2f} h"
                    )
